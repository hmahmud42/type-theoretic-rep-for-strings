"""
Defines some basic locaction checkers.
"""

def const_sequential(inc, locs):
    for i in range(len(locs)-1):
        if locs[i+1] - locs[i] != inc:
            return False
    return True


def max_const_sequential(inc, locs):
    for i in range(len(locs)-1):
        if locs[i+1] - locs[i] <= inc:
            return False
    return True


def var_sequential(incs, locs):
    for i in range(len(locs)-1):
        if locs[i+1] - locs[i] != incs[i]:
            return False
    return True


def max_var_sequential(incs, locs):
    for i in range(len(locs)-1):
        if locs[i+1] - locs[i] <= incs[i]:
            return False
    return True


def const_graph(inc, locs):
    for i in range(len(locs)-1):
        if locs[i+1][0] - locs[i][0] != inc[0] and \
            locs[i+1][1] - locs[i][1] != inc[1]:
            return False
    return True


def max_const_graph(inc, locs):
    for i in range(len(locs)-1):
        if locs[i+1][0] - locs[i][0] <= inc[0] and \
            locs[i+1][1] - locs[i][1] <= inc[1]:
            return False
    return True


def var_graph(incs, locs):
    for i in range(len(locs)-1):
        if locs[i+1][0] - locs[i][0] != incs[i][0] and \
            locs[i+1][1] - locs[i][1] != incs[i][1]:
            return False
    return True


def max_var_sequential(incs, locs):
    for i in range(len(locs)-1):
        if locs[i+1][0] - locs[i][0] <= incs[i][0] and \
            locs[i+1][1] - locs[i][1] <= incs[i][1]:
            return False
    return True








