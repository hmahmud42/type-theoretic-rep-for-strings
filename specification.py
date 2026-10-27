"""
Core definitions for specifications.
"""


from constraint import Constraint
from typing import Any, Callable
from types import MethodType
from constraint import Constraint
from dataclasses import dataclass



class BaseSpec:
    def __init__(self, value: Any, diff_func: Callable[[Any, Any], float]):
        self.level = 0
        self.value = value
        self.tup_value = tuple(value)
        self.diff_func = MethodType(diff_func, self)


class SatStats:
    def __init__(self, cur_loc):
        self.cur_loc = cur_loc
        self.total_diff = 0
        self.locs = []
        self.patts = []

    def update_patt_stats(self, input_patts, loc, diff, nxt_inc):
        self.patts.append(input_patts[loc])
        self.locs.append(loc)
        self.total_diff += diff
        self.cur_loc = loc + nxt_inc



class Spec:
    def __init__(self, level: int, constraint: Constraint, diff_func: Callable[[Any, Any], int]):
        self.level = level
        self.constraint = constraint
        self.diff_func = MethodType(diff_func, self)

    def _check_sat(self, cur_patt, total_diff):
        diff = self.constraint.root_pattern.diff_func(cur_patt)
        if diff > self.constraint.max_diff: return False, diff
        if diff + total_diff > self.constraint.total_diff: return False, diff
        return True, diff

    def check(self, input_patts: list[Any], at: int) -> bool:
        sat_stats = SatStats(at)

        patt_holds = True
        while patt_holds:
            patt_holds = False
            for loc in range(sat_stats.cur_loc, sat_stats.cur_loc+self.constraint.srch_inc):
                if loc >= len(input_patts):
                    patt_holds = False
                    break
                sat, diff = self._check_sat(input_patts[loc], sat_stats.total_diff)
                if sat: 
                    sat_stats.update_patt_stats(input_patts, loc, diff, self.constraint.nxt_inc)
                    patt_holds = True
                    break

        if len(sat_stats.locs) > self.constraint.min_len: 
            return True, sat_stats.locs, sat_stats.patts, sat_stats.total_diff
        return False, sat_stats.locs, sat_stats.patts, sat_stats.total_diff




def int_hamming(l1: list[int], l2: list[int]) -> int:
    v = 0
    for a, b in zip(l1, l2):
        v += int(a !=b )
    return v


def bp_diff(self, bp):
    """
    Hamming distance between different base pattern based on the tuple values.
    """
    return int_hamming(self.value, bp.value)

def seq_diff(self, patt):
    """
    Distance between higher level patterns
    """
    return self.root_patt.diff_func(patt.root_patt) + self.constraint.numeric_diff(patt.constraint)


