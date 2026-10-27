import numpy as np


from collections import defaultdict, Counter

class PrefixTreeDistribution:
    def __init__(self, alphabet, max_length, distributions=None):
        """
        alphabet: list/tuple of symbols (e.g., [0, 1] or ['a', 'b'])
        max_length: maximum sequence length (M)
        distributions: list of tuples (prefix, prob_array) defining conditional distributions
        """
        self.alphabet = list(alphabet)
        self.alphabet_size = len(self.alphabet)
        self.symbol_to_idx = {sym: i for i, sym in enumerate(self.alphabet)}
        self.max_length = max_length
        self.tree = {}
        self.default_dist = np.full(self.alphabet_size, 1.0 / self.alphabet_size)

        if distributions:
            self._build_from_array(distributions)

    def _build_from_array(self, distributions):
        for prefix, prob_list in distributions:
            prob_arr = np.array(prob_list, dtype=float)
            # Normalize to guarantee a valid probability distribution
            prob_arr = prob_arr / np.sum(prob_arr)
            
            if prefix == "default":
                self.default_dist = prob_arr
            else:
                prefix_tuple = tuple(prefix)
                if len(prefix_tuple) <= self.max_length:
                    self.tree[prefix_tuple] = prob_arr

    def get_distribution(self, prefix):
        """Returns P(next_symbol | trailing_prefix_context)."""
        prefix_tuple = tuple(prefix)
        
        # Keep only the last max_length symbols
        if len(prefix_tuple) > self.max_length:
            prefix_tuple = prefix_tuple[-self.max_length:]
        
        # Back-off strategy: try full context, shorten context if missing, or use default
        while len(prefix_tuple) > 0:
            if prefix_tuple in self.tree:
                return self.tree[prefix_tuple]
            prefix_tuple = prefix_tuple[1:]  # Drop oldest symbol
        
        return self.tree.get((), self.default_dist)

    def log_likelihood(self, sequence):
        """Computes log P(sequence) assuming sequence length is fixed externally."""
        log_prob = 0.0
        for i in range(len(sequence)):
            prefix = sequence[:i]
            next_symbol = sequence[i]
            dist = self.get_distribution(prefix)
            symbol_idx = self.symbol_to_idx[next_symbol]
            log_prob += np.log(dist[symbol_idx])

        return log_prob

    def fit(self, data, smoothing=1.0):
        """
        Maximum Likelihood Estimation with additive (Laplace) smoothing.
        Uses a sliding context window bounded by self.max_length.
        """
        counts = defaultdict(lambda: np.zeros(self.alphabet_size))
        total_counts = np.zeros(self.alphabet_size)

        for seq in data:
            for i in range(len(seq)):
                # Retain only the trailing max_length symbols as context
                start_idx = max(0, i - self.max_length)
                prefix = tuple(seq[start_idx:i])
    
                next_symbol_idx = self.symbol_to_idx[seq[i]]
                counts[prefix][next_symbol_idx] += 1
                total_counts[next_symbol_idx] += 1

        # Estimate prefix-specific distributions
        self.tree = {}
        for prefix, symbol_counts in counts.items():
            smoothed_counts = symbol_counts + smoothing
            self.tree[prefix] = smoothed_counts / np.sum(smoothed_counts)

        # Estimate global fallback default distribution
        smoothed_totals = total_counts + smoothing
        self.default_dist = smoothed_totals / np.sum(smoothed_totals)

    def sample(self, length):
        """Generates a list of symbols of a given length."""
        sequence = []
        for _ in range(length):
            # prefix = sequence[:self.max_length]
            prefix = sequence[-self.max_length:]            
            dist = self.get_distribution(prefix)
            next_symbol = np.random.choice(self.alphabet, p=dist)
            sequence.append(int(next_symbol))
        return sequence


def gen_pref_data(size, seq_length, with_models=False):

    alphabet = [0, 1]
    
    custom_dists_1 = [
        ([1, 0, 1], [0.5, 0.5]),
        ([1, 0, 0], [0.7, 0.3]),
        ("default", [0.1, 0.9])
    ]
    model_1 = PrefixTreeDistribution(alphabet=alphabet, max_length=3, distributions=custom_dists_1)

    custom_dists_2 = [
        ([1, 0, 1], [0.1, 0.9]),
        ([1, 0, 0], [0.3, 0.7]),
        ("default", [0.5, 0.5])
    ]
    model_2 = PrefixTreeDistribution(alphabet=alphabet, max_length=3, distributions=custom_dists_2)

    models = [model_1, model_2]

    Ys = np.random.randint(0, 2, size=size)
    Xs = [models[y].sample(length=seq_length) for y in Ys]

    if not with_models:
        return Ys, Xs
    else:
        return Ys, Xs, models 


class PrefixTreeClassifier:
    def __init__(self, alphabet, max_length, smoothing=1.0):
        """
        alphabet: list/tuple of symbols (e.g., [0, 1] or ['a', 'b'])
        max_length: maximum prefix length for underlying trees
        smoothing: additive Laplace smoothing parameter for tree estimation
        """
        self.alphabet = list(alphabet)
        self.max_length = max_length
        self.smoothing = smoothing
        self.classes = []
        self.class_priors = {}
        self.models = {}

    def fit(self, X, y):
        """
        Fits a PrefixTreeDistribution for each unique class in y.
        X: list of sequences
        y: list/array of class labels
        """
        self.classes = np.unique(y)
        total_samples = len(y)
        class_counts = Counter(y)

        # Calculate class prior probabilities P(Y=c)
        for c in self.classes:
            self.class_priors[c] = class_counts[c] / total_samples

            # Partition data by class label
            X_c = [X[i] for i in range(total_samples) if y[i] == c]

            # Fit prefix tree distribution for class c
            model_c = PrefixTreeDistribution(
                alphabet=self.alphabet,
                max_length=self.max_length
            )
            model_c.fit(X_c, smoothing=self.smoothing)
            self.models[c] = model_c

    def predict_joint_log_likelihood(self, sequence):
        """
        Computes log P(x, Y=c) = log P(x | Y=c) + log P(Y=c) for each class c.
        """
        joint_log_probs = {}
        for c in self.classes:
            log_prior = np.log(self.class_priors[c])
            log_likelihood = self.models[c].log_likelihood(sequence)
            joint_log_probs[c] = log_prior + log_likelihood
        return joint_log_probs

    def predict_proba(self, sequence):
        """
        Computes posterior class probabilities P(Y=c | x) using log-sum-exp stabilization.
        """
        joint_logs = self.predict_joint_log_likelihood(sequence)
        
        # Numerical stability shift via max log trick
        max_log = max(joint_logs.values())
        unnormalized_probs = {
            c: np.exp(log_p - max_log) for c, log_p in joint_logs.items()
        }
        
        total_mass = sum(unnormalized_probs.values())
        return {c: prob / total_mass for c, prob in unnormalized_probs.items()}

    def predict_single(self, sequence):
        """Predicts the class label with the highest posterior probability."""
        posterior_probs = self.predict_proba(sequence)
        return max(posterior_probs, key=posterior_probs.get)

    def predict(self, Xs):
        """Predicts the class label with the highest posterior probability."""
        return np.array([self.predict_single(x) for x in Xs])



# Example Usage
if __name__ == "__main__":
    alphabet = [0, 1]
    max_len = 3

    # 1. Instantiate with custom distributions
    custom_dists = [
        ([1, 0, 1], [0.5, 0.5]),
        ([1, 0, 0], [0.7, 0.3]),
        ("default", [0.1, 0.9])
    ]
    model = PrefixTreeDistribution(alphabet=alphabet, max_length=max_len, distributions=custom_dists)

    # Sample from configured distribution
    sampled_seq = model.sample(length=5)
    print("Sampled Sequence:", sampled_seq)
    print("Log Likelihood:", model.log_likelihood(sampled_seq))

    # 2. Fit model distributions from data
    training_data = [
        [1, 1, 1, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 0, 1, 1, 0],
        [0, 1, 0, 0, 1]
    ]
    
    fitted_model = PrefixTreeDistribution(alphabet=alphabet, max_length=max_len)
    fitted_model.fit(training_data, smoothing=1.0)
    
    print("\nLearned Distribution for prefix (1, 0, 1):", fitted_model.get_distribution([1, 0, 1]))
    print("Learned Default Distribution:", fitted_model.default_dist)

    Ys, Xs = gen_pref_data(size=20, seq_length=10)

    print(f"\n\n\n")
    for y, x in zip(Ys, Xs):
        if y == 0:
            print(f"{x}: {y}")

    print(f"\n----\n")

    for y, x in zip(Ys, Xs):
        if y == 1:
            print(f"{x}: {y}")


