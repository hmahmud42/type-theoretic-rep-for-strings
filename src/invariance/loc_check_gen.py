"""
Iterator versions of location checkers - these generates sequences
that satisfe the constraints
"""

def const_sequential_gen(inc, max_len, last_locs):
    if len(last_locs) > max_len: return None
    return last_locs[-1] + inc


def max_const_sequential_gen(inc, max_len, last_locs):
    if len(last_locs) > max_len: return None
    ll = last_locs[-1] 
    return [ll + i+1 for i in range(inc)]


def var_sequential_gen(incs, last_locs):
    if len(last_locs) > len(incs): return None
    return last_locs[-1] + incs[len(last_locs) - 1]


def max_var_sequential_gen(incs, last_locs):
    if len(last_locs) > len(incs): return None
    return [last_locs[-1] + i for i in range(incs[len(last_locs) - 1])]


def const_graph_gen(inc, max_len, last_locs):
    if len(last_locs) > max_len: return None
    return [last_locs[-1][0] + inc[0], last_locs[-1][1] + inc[1]]


def max_const_graph_gen(inc, max_len, last_locs):
    if len(last_locs) > max_len: return None
    return [[last_locs[-1][0] + row_inc, last_locs[-1][1] + col_inc] 
            for row_inc in range(inc[0]) for col_inc in range(inc[1])]


def var_graph_gen(incs, last_locs):
    if len(last_locs) >= len(incs): return None
    idx = len(last_locs) - 1
    return [last_locs[-1][0] + incs[idx][0], 
            last_locs[-1][1] + incs[idx][1]]


def max_var_graph_gen(incs, last_locs):
    if len(last_locs) >= len(incs): return None
    idx = len(last_locs) - 1
    return [
        [last_locs[-1][0] + row_inc, last_locs[-1][1] + col_inc] 
        for row_inc in range(incs[idx][0]) 
        for col_inc in range(incs[idx][1])
        ]









