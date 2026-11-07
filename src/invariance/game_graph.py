import numpy as np
from scipy.spatial.distance import euclidean

# =====================================================================
# DATASTRUCTURES & CORE MOMENT UTILITIES
# =====================================================================

class Node:
    """Represents a player/node at any layer in the hierarchical graph."""
    def __init__(self, node_id, patches, locations):
        self.id = node_id
        self.patches = patches if isinstance(patches, list) else [patches]
        self.locations = locations if isinstance(locations, list) else [locations]
        self.count = len(self.patches)

        # 1. Spatial Centroid
        locs_arr = np.array(self.locations, dtype=float)
        self.mean_loc = np.mean(locs_arr, axis=0)

        # 2. Spatial Covariance Matrix (2x2)
        if self.count > 1:
            self.cov_loc = np.cov(locs_arr, rowvar=False)
            if self.cov_loc.ndim == 0:
                self.cov_loc = np.array([[float(self.cov_loc), 0.0], [0.0, 0.0]])
        else:
            self.cov_loc = np.zeros((2, 2))

        # 3. Pixel Mean and Pixel Variance Patches
        patch_stack = np.stack(self.patches, axis=0)
        self.mean_patch = np.mean(patch_stack, axis=0)
        self.var_patch = np.var(patch_stack, axis=0)

    @property
    def payload_vector(self):
        """Returns flattened attribute payload for distance computations."""
        return np.hstack([
            self.mean_loc,
            self.cov_loc.flatten(),
            self.mean_patch.flatten(),
            self.var_patch.flatten()
        ])

    def __repr__(self):
        return f"Node_{self.id}(K={self.count}, loc={np.round(self.mean_loc, 2)})"


class GraphRepresentation:
    """Container for the output of Protocol 1."""
    def __init__(self, shape_name, nodes):
        self.shape_name = shape_name
        self.nodes = nodes
        self.adjacency = self._build_adjacency()

    def _build_adjacency(self, dist_thresh=3.5):
        """Builds neighborhood adjacency matrix based on spatial centroid distance."""
        N = len(self.nodes)
        adj = np.zeros((N, N), dtype=bool)
        for i in range(N):
            for j in range(i + 1, N):
                if euclidean(self.nodes[i].mean_loc, self.nodes[j].mean_loc) < dist_thresh:
                    adj[i, j] = True
                    adj[j, i] = True
        return adj


# =====================================================================
# PROTOCOL 1: REPRESENTATION & AGGREGATION GAME
# =====================================================================

def node_distance(nodeA, nodeB, alpha=0.4, beta=0.3, gamma=0.3):
    """Evaluates payload invariance cost f_L1(A, B)."""
    loc_dist = euclidean(nodeA.mean_loc, nodeB.mean_loc)
    cov_dist = float(np.linalg.norm(nodeA.cov_loc - nodeB.cov_loc, ord='fro'))
    patch_dist = float(np.linalg.norm(nodeA.mean_patch - nodeB.mean_patch, ord='fro'))
    return alpha * loc_dist + beta * cov_dist + gamma * patch_dist


def protocol_1_aggregate(matrix, patch_size=(2, 2), theta=3.5):
    """
    Executes Protocol 1: Bottom-up coalition formation game to generate
    hierarchical graph representation G from a binary matrix.
    """
    H, W = matrix.shape
    pH, pW = patch_size

    # Layer 0: Initialize base patch players
    nodes = []
    pid = 0
    for r in range(0, H - pH + 1, pH):
        for c in range(0, W - pW + 1, pW):
            patch = matrix[r:r+pH, c:c+pW]
            # Prune completely empty background patches
            if np.sum(patch) > 0:
                nodes.append(Node(f"L0_{pid}", patch, (r, c)))
                pid += 1

    # Layer 1 Dynamic Coalition Game (Hedonic Nash Equilibrium)
    merged = set()
    layer1_nodes = []
    l1_id = 0

    for i in range(len(nodes)):
        if i in merged:
            continue
        best_j, best_cost = None, float('inf')
        for j in range(i + 1, len(nodes)):
            if j in merged:
                continue
            cost = node_distance(nodes[i], nodes[j])
            if cost < theta and cost < best_cost:
                best_cost = cost
                best_j = j

        if best_j is not None:
            merged.update([i, best_j])
            comb_patches = nodes[i].patches + nodes[j].patches
            comb_locs = nodes[i].locations + nodes[j].locations
            layer1_nodes.append(Node(f"L1_{l1_id}", comb_patches, comb_locs))
            l1_id += 1
        else:
            merged.add(i)
            layer1_nodes.append(nodes[i])

    return GraphRepresentation("ExtractedGraph", layer1_nodes)


# =====================================================================
# PROTOCOL 3: TEMPLATE INDUCTION & CONTRASTIVE LEARNING
# =====================================================================

class Template:
    """Class Template holding consensus node payloads derived via Protocol 3."""
    def __init__(self, class_name, node_payloads):
        self.class_name = class_name
        self.node_payloads = node_payloads  # List of feature vectors


def protocol_3_learn_templates(class_graphs_dict, eta=0.2):
    """
    Executes Protocol 3: Cross-graph matching for Positive (+Δ) and Negative (-Δ) learning.
    - Positive Learning: Consolidates common class features.
    - Negative Learning: Suppresses non-discriminative features shared across classes.
    """
    templates = {}

    # Step 1: Positive Learning (+Δ) within each class
    for class_name, graphs in class_graphs_dict.items():
        all_payloads = []
        for g in graphs:
            for n in g.nodes:
                all_payloads.append(n.payload_vector)
        
        # Mean consensus feature representation for the class
        consensus_payloads = np.mean(all_payloads, axis=0, keepdims=True)
        templates[class_name] = Template(class_name, consensus_payloads)

    # Step 2: Negative Learning (-Δ) across different classes
    class_names = list(templates.keys())
    if len(class_names) >= 2:
        for i in range(len(class_names)):
            for j in range(i + 1, len(class_names)):
                c1, c2 = class_names[i], class_names[j]
                # Compute cross-class overlap delta
                shared_delta = eta * (templates[c1].node_payloads - templates[c2].node_payloads)
                # Penalize non-discriminative overlap
                templates[c1].node_payloads -= eta * shared_delta
                templates[c2].node_payloads += eta * shared_delta

    return templates


# =====================================================================
# PROTOCOL 2: GRAPH MATCHING & INFERENCE GAME
# =====================================================================

def protocol_2_inference(graph_G, template_T, gamma=0.3):
    """
    Executes Protocol 2: Bipartite matching game between Graph G and Reference Template T.
    Evaluates both direct attribute payload matching and neighborhood structural coherence.
    Returns the total Nash Equilibrium alignment score.
    """
    N_G = len(graph_G.nodes)
    N_T = len(template_T.node_payloads)

    # Strategy space: Initialize random/greedy initial match assignments
    assignments = np.zeros(N_G, dtype=int)

    # Parallel Best-Response Iterations until Nash Equilibrium
    changed = True
    max_iters = 20
    iters = 0

    while changed and iters < max_iters:
        changed = False
        iters += 1
        for i in range(N_G):
            best_target = assignments[i]
            best_utility = -float('inf')

            for j in range(N_T):
                # 1. Direct Attribute Payload Similarity
                payload_i = graph_G.nodes[i].payload_vector
                payload_j = template_T.node_payloads[j]
                direct_match = 1.0 / (1.0 + float(np.linalg.norm(payload_i - payload_j)))

                # 2. Immediate Neighborhood Structural Alignment
                neighbors_i = np.where(graph_G.adjacency[i])[0]
                nbr_score = 0.0
                if len(neighbors_i) > 0:
                    nbr_payloads = [graph_G.nodes[nbr].payload_vector for nbr in neighbors_i]
                    nbr_score = np.mean([
                        1.0 / (1.0 + float(np.linalg.norm(p_nbr - payload_j)))
                        for p_nbr in nbr_payloads
                    ])

                # Total Utility U_i
                utility = direct_match + gamma * nbr_score

                if utility > best_utility:
                    best_utility = utility
                    best_target = j

            if assignments[i] != best_target:
                assignments[i] = best_target
                changed = True

    # Compute Total Inference Confidence Score at Nash Equilibrium
    total_score = 0.0
    for i in range(N_G):
        j = assignments[i]
        p_i = graph_G.nodes[i].payload_vector
        p_j = template_T.node_payloads[j]
        total_score += 1.0 / (1.0 + float(np.linalg.norm(p_i - p_j)))

    return total_score


# =====================================================================
# DEMONSTRATION RUN: END-TO-END PIPELINE
# =====================================================================

if __name__ == "__main__":
    print("=====================================================================")
    print(" THREE-PROTOCOL GAME-THEORETIC PIPELINE DEMONSTRATION")
    print("=====================================================================\n")

    # 1. Define Binary Shape Training Samples (Letter 'T' and Letter 'L')
    t_shape_1 = np.array([
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ])

    l_shape_1 = np.array([
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ])

    # -----------------------------------------------------------------
    # STEP 1: EXECUTE PROTOCOL 1 (Representation / Graph Generation)
    # -----------------------------------------------------------------
    print("--- PROTOCOL 1: Generating Graph Representations ---")
    graph_T1 = protocol_1_aggregate(t_shape_1, theta=3.5)
    graph_L1 = protocol_1_aggregate(l_shape_1, theta=3.5)
    print(f"Graph 'T1' generated with {len(graph_T1.nodes)} higher-order collective nodes.")
    print(f"Graph 'L1' generated with {len(graph_L1.nodes)} higher-order collective nodes.\n")

    # -----------------------------------------------------------------
    # STEP 2: EXECUTE PROTOCOL 3 (Template Induction & Learning)
    # -----------------------------------------------------------------
    print("--- PROTOCOL 3: Learning Templates via Positive/Negative Games ---")
    training_data = {
        "Class_T": [graph_T1],
        "Class_L": [graph_L1]
    }
    learned_templates = protocol_3_learn_templates(training_data, eta=0.2)
    print("Learned Templates generated:")
    for name, tmpl in learned_templates.items():
        print(f"  Template '{name}': Payload Shape = {tmpl.node_payloads.shape}")
    print()

    # -----------------------------------------------------------------
    # STEP 3: EXECUTE PROTOCOL 2 (Inference on Unseen Test Input)
    # -----------------------------------------------------------------
    print("--- PROTOCOL 2: Inference & Graph Matching Game ---")
    # Test Input: A noisy 'T' shape
    t_test_noisy = t_shape_1.copy()
    t_test_noisy[7, 1] = 1  # Add isolated noise pixel

    test_graph = protocol_1_aggregate(t_test_noisy, theta=3.5)
    print(f"Test Input (Noisy 'T') processed into {len(test_graph.nodes)} graph nodes.")

    # Match Test Graph against both learned templates via Protocol 2
    score_T = protocol_2_inference(test_graph, learned_templates["Class_T"])
    score_L = protocol_2_inference(test_graph, learned_templates["Class_L"])

    print("\nInference Alignment Scores (Nash Equilibrium Payoffs):")
    print(f"  Match Score against Class_T Template : {score_T:.4f}")
    print(f"  Match Score against Class_L Template : {score_L:.4f}")

    predicted_class = "Class_T" if score_T > score_L else "Class_L"
    print(f"\nFINAL CLASSIFICATION RESULT: {predicted_class}")
    print("=====================================================================")