"""
Creates invariance graph from a single image
"""
from invariance_graph import InvarianceGraph
from invariance.invariance_base import ConcInvarianceBase
from utils import base_inv_diff


def get_base_invariances(x, cur_map, patt_len=4):
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

    base_inv_list = []
    for i in range(len(x) - patt_len):
        base_inv = ConcInvarianceBase(value=x[i:i+patt_len], 
                                diff_func=base_inv_diff)
        if cur_map is not None:
            if base_inv.tup_value in cur_map:
                base_inv_list.append(cur_map[base_inv.tup_value])
            else:
                base_inv_list.append(base_inv)
                cur_map[base_inv.tup_value] = base_inv
        else:
            base_inv_list.append(base_inv)
    return base_inv_list


def generate_next_level(x, K, levels, base_elements):
    ...


def create_invariance_graph(x, K, patt_len=4):
    cur_map = dict()
    base_elements = get_base_invariances(x, cur_map={}, patt_len=patt_len)
    new_generated = True
    levels = []
    inv_graph = InvarianceGraph()
    while new_generated:
        level = generate_next_level(x, K, levels, base_elements)
        
        if len(level) > 0:
            new_generated = len(level) > 0
            inv_graph.add_layer(level)
    
    return inv_graph






