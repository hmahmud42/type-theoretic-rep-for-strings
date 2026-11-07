"""
Experimental implementation of the layer graph structure for 
implementation.
"""
from abc import ABC, abstractmethod
from invariance.invariance_diff import ConcInvBaseMaxDiffMin
from invariance.invariance_base import ConcInvarianceBase
from utils import base_inv_diff

class InvarianceGraphLayer:

    def __init__(self, conn_matrix, row_map, col_map):
        """
        Docstring for __init__
        
        Parameters
        -----------
        conn_matrix:
            Binary matrix of the graph layer
        
        row_map: dict[int, ConcInv]
            Maps the each to the corresponding concrete invariance.
        
        col_map: dict[int, ConcInv]
            Maps each column index to the corresponding concrete invariance
        """
        self.conn_matrix = conn_matrix
        self.row_map = row_map
        self.col_map = col_map


class InvarianceGraph:
    def __init__(self, graph_layers):
        self.graph_layers = graph_layers

    def add_level(self, level):
        ...




def basic_graph_test():
    # example of a simple graph for testing 
    base_1 = ConcInvarianceBase(value=(1, 0, 0, 1),
                            loc=0,
                            diff_func=base_inv_diff)

    base_2 = ConcInvarianceBase(value=(1, 0, 1, 1),
                            loc=32,
                            diff_func=base_inv_diff)


    conc_inv = ConcInvBaseMaxDiffMin(diff_val=1, min_len=2)

    row_map = {0: base_1, 1: base_2}
    col_map = {0: conc_inv}

    conn_matrix = [[1], [1]]

    graph_layer = InvarianceGraphLayer(
        conn_matrix=conn_matrix, row_map=row_map, col_map=col_map)



def type_check_all(container, targ_inv, input_invs):
    """
    Creates a set of arguments that can be fed into the
    invarance targ_invs to create concrete invariances. 
    
    Parameters
    ----------

    targ_invariance:
        The target invariance

    input_invs: list
        The set of input invariances
    """
    container.reset()
    tree = dict()
    type_check_state = {"complete": False}
    root = input_invs[0]
    if targ_inv.type_check(type_check_state, [root]):
        container.add((root, type_check_state))
        tree["root"] = root
    else:
        return [], tree

    args_list = [] 
    # this is probably better handled through a recursive call.
    while not container.isempty():
        current, tc_state = container.next()
        
















