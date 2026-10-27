"""
Create the first version of the system for strings
"""

from __future__ import annotations
from typing import Any, Callable
from dataclasses import dataclass
from types import MethodType
from collections import defaultdict

from sklearn.naive_bayes import CategoricalNB, BernoulliNB
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from scipy.stats import entropy

from prefix_tree import gen_pref_data, PrefixTreeDistribution, PrefixTreeClassifier
from constraint import Constraint
from specification import BaseSpec, Spec, bp_diff



def create_base_pattern_list(seq, patt_len, diff_func, cur_map=None):
    """
    Create a list of base patterns from the given sequences.

    Parameters
    ----------
    seq: 
        List of data

    patt_len:
        Length of each pattern

    diff_func:
        The diff-function for these patterns
    
    cur_map:
        mapping from tuple value to the base pattern
    """

    bp_list = []
    for i in range(len(seq) - patt_len):
        bp = BaseSpec(seq[i:i+patt_len], diff_func)
        if cur_map is not None:
            if bp.tup_value in cur_map:
                bp_list.append(cur_map[bp.tup_value])
            else:
                bp_list.append(bp)
                cur_map[bp.tup_value] = bp
        else:
            bp_list.append(bp)
    return bp_list


def get_base_spec_Xs(Xs, patt_len, debug=False):
    """
    Get all the base patterns from a Xs dataset. 
    """
    cur_map = dict()
    base_patterns_per_x = [create_base_pattern_list(x, patt_len, bp_diff, cur_map) for x in Xs]
    if debug:
        print(f"Observed patterns in data:")
        for k in cur_map.keys():
            print(k)

    bp_Xs = [ [bp.tup_value for bp in bpx] for bpx in base_patterns_per_x]
    bp_Xs = [ [int(k in bpx) for k in cur_map.keys()] for bpx in bp_Xs] 

    return bp_Xs, cur_map


def create_max_diff_patterns(bp_x, max_diff_values):
    patt = []
    for md in max_diff_values:
        for loc in range(len(bp_x)-4):
            cur_md = 0
            for bpp_x in bp_x[loc:loc+4]:
                cur_md = max(cur_md, bp_x[loc].diff_func(bpp_x))
            if cur_md <= md:
                patt.append(1)
            else:
                patt.append(0)
    return patt


def get_spec_Xs(Xs, patt_len, debug=False):
    """
    Get all the base patterns from a Xs dataset. 
    """
    cur_map = dict()
    base_patterns_per_x = [create_base_pattern_list(x, patt_len, bp_diff, cur_map) for x in Xs]
    max_diff_values = [1]
    mdp_per_x = [create_max_diff_patterns(bp_x, max_diff_values) for bp_x in base_patterns_per_x]

    if debug:
        print(f"Observed patterns in data:")
        for k in cur_map.keys():
            print(k)

    bp_Xs = [ [bp.tup_value for bp in bpx] for bpx in base_patterns_per_x]
    bp_Xs = [ [int(k in bpx) for k in cur_map.keys()] + mdp_x for bpx, mdp_x in zip(bp_Xs, mdp_per_x)] 

    return bp_Xs, cur_map, mdp_per_x




def learn_base_spec_classifier(patt_len=3, round="", debug=True):
    """
    Create a Naive Bayes classifier over the base patterns only
    """
    sample_size = 1000
    train_size = 800

    print(f"\n****\nNow Learning {round}")

    Ys, Xs, models = gen_pref_data(size=sample_size, seq_length=20, with_models=True)
    bp_Xs, _, mdp_per_x = get_spec_Xs(Xs, patt_len, debug)
    print(f"mean value of ys {np.mean(Ys)}")
    # print(np.var(mdp_per_x, axis=0))

    # print(bp_Xs[0])

    classifier = BernoulliNB()
    classifier.fit(bp_Xs[0:train_size], Ys[0:train_size])
    # classifier.fit(mdp_per_x[0:train_size], Ys[0:train_size])
    # preds = classifier.predict(mdp_per_x[train_size:])
    preds = classifier.predict(bp_Xs[train_size:])
    error = np.mean(preds != Ys[train_size:])

    # classifier_whole = DecisionTreeClassifier()
    # classifier_whole.fit(Xs[0:train_size], Ys[0:train_size])
    # preds_whole = classifier_whole.predict(Xs[train_size:])
    # error_whole = np.mean(preds_whole != Ys[train_size:])


    if debug:
        print(f"Prediction error on train data: {error}")
    # print(f"Prediction error on test data for whole: {error_whole}")

    pfc = PrefixTreeClassifier(alphabet=[0,1], max_length=3)
    pfc.fit(Xs[0:train_size], Ys[0:train_size])
    # pfc.models[0] = models[0]
    # pfc.models[1] = models[1]
    pfc_preds = pfc.predict(Xs[train_size:])
    pfc_err = np.mean(pfc_preds != Ys[train_size:])
    print(f"Error of prefix tree classifier {pfc_err}")  

    return error


def create_spec_from_seq(patt_seq, loc_seq):
    """
    Given a sequence of patterns and locations creates the pattern 
    satisfying the constraints represented by the sequence.
    """
    root = patt_seq[0]
    diffs = [root.diff_func(p) for p in patt_seq]
    sorted_locs = sorted(loc_seq)
    constraint = Constraint(
        root_pattern=patt_seq[0],
        max_diff=max(diffs),
        total_diff=sum(diffs),
        nxt_inc=1,
        srch_inc=max(b - a for a, b in zip(sorted_locs, sorted_locs[1:])),
        min_len=1,
        max_len=len(patt_seq)
    )

    return Spec(1, constraint=constraint, diff_func=seq_diff)


def get_base_spec_entropies(Ys, bp_Xs, num_class=2):
    """
    Compute entropy over classes given for each base pattern 
    """
    bp_count = defaultdict(lambda : np.zeros(num_class))
    for y, bp_x in zip(Ys, bp_Xs):
        for bp_idx in range(len(bp_x)):
            if bp_x[bp_idx] > 0:
                bp_count[bp_idx][y] += 1

    bp_ent = dict()
    for bp_idx in bp_count:
        bp_ent[bp_idx] = entropy(bp_count[bp_idx]*1.0 / np.sum(bp_count[bp_idx]))

    print(bp_count)

    return bp_ent


def get_base_spec_pair_entropies(Ys, bp_Xs, num_class=2):
    """
    Compute entropy over classes given for each base pattern 
    """
    bp_pair_count = defaultdict(lambda : np.zeros(num_class))
    for y, bp_x in zip(Ys, bp_Xs):
        for bp_idx_1 in range(len(bp_x)):
            for bp_idx_2 in range(len(bp_x)):
                if bp_x[bp_idx_1] > 0 and bp_x[bp_idx_2] > 0:
                    bp_pair_count[(bp_idx_1, bp_idx_2)][y] += 1

    bp_pair_ent = dict()
    for bp_pair in bp_pair_count:
        bp_pair_ent[bp_pair] = entropy(bp_pair_count[bp_pair]*1.0 / np.sum(bp_pair_count[bp_pair]))


    return bp_pair_ent



def gen_patt_sample():
    ...


def run_learn_exp():
    print("\n****\nStarting Learning Experiments\n")

    patt_len = 5
    rounds = 10
    print(f"\n --> Starting Naive Bayes learning with bas pattern of length {patt_len} for {rounds} rounds \n")

    errs = []
    for r  in range(rounds):
        errs.append(learn_base_spec_classifier(patt_len=patt_len,round=r, debug=False))
    print(f"Mean error over {rounds} rounds: {np.mean(errs)}")
    print(f"Variance of error over {rounds} rounds: {np.var(errs)}")




def main():

    run_learn_exp()
    # base_spec_1 = BaseSpec([0, 1, 1], diff_func=bp_diff)
    # base_spec_2 = BaseSpec([1, 1, 1], diff_func=bp_diff)
    # print(base_spec_1.diff_func(base_spec_2))

    # patt_constraint = Constraint(            
    #     root_pattern=base_spec_1, 
    #     max_diff=1, 
    #     total_diff=2,
    #     nxt_inc=1,
    #     srch_inc=2,
    #     min_len=1,
    #     max_len=3,
    # )

    # patt = Spec(level=1, constraint=patt_constraint, diff_func=seq_diff)    
    # v = patt.check([base_spec_1, base_spec_2, base_spec_2], 0)
    # print(v)

    # seq = [1, 0, 1, 0, 1, 0, 1, 0]
    # cur_map = dict()
    # bps = create_base_pattern_list(seq, 3, bp_diff, None)
    # print()
    # for bp in bps:
    #     print(bp.value)

    # print(bps)

    # # run_learn_exp()

    # base_patt_3 = BaseSpec([0, 0, 1], diff_func=bp_diff)
    # base_patt_4 = BaseSpec([0, 0, 0], diff_func=bp_diff)

    # bp_list = [base_spec_1, base_spec_2, base_patt_3, base_patt_4] 

    # level_1_patt = create_spec_from_seq(bp_list, [0, 1, 4, 6])

    # print(level_1_patt)

    

    # from IPython import embed
    # embed()

    # Ys, Xs, models = gen_pref_data(size=1000, seq_length=20, with_models=True)
    # bp_Xs, cur_map = get_bp_Xs(Xs, patt_len=6)

    # bp_ent = get_base_feature_entropies(Ys, bp_Xs)
    # sorted_data = dict(sorted(bp_ent.items(), key=lambda item: item[1]))
    # idx_to_val = {i:k for i, k in enumerate(cur_map.keys())}

    # print("\nEntropies are:")
    # for k in sorted_data.keys():
    #     print(f"{k}: {idx_to_val[k]} -> {sorted_data[k]}")
    
    # bp_pair_ent = get_base_feature_pair_entropies(Ys, bp_Xs)

    # print("\n\nPair Entropies are:")
    # sorted_data = dict(sorted(bp_pair_ent.items(), key=lambda item: item[1]))
    # for k in sorted_data.keys():
    #     print(f"{k} -> {sorted_data[k]}")

    






if __name__ == '__main__':
    main()

