import copy

class Constraint:
    def __init__(self, 
                 root_pattern, 
                 max_diff: int, 
                 total_diff: int, 
                 nxt_inc: int,
                 srch_inc: int, 
                 min_len:int, 
                 max_len: int
                 ):
        self.root_pattern = root_pattern
        self.max_diff = max_diff
        self.total_diff = total_diff

        if self.max_diff > self.total_diff:
            print(f"WARNING: in Constraint.__init__, parameter max_diff = {max_diff} is greater than total_diff = {total_diff}")

        self.nxt_inc = nxt_inc
        self.srch_inc = srch_inc
        self.min_len = min_len
        self.max_len = max_len  

    def numeric_diff(self, c):
        return abs(self.max_diff - c.max_diff) + abs(self.total_diff - c.total_diff) + \
               abs(self.nxt_inc - c.nxt_inc) + abs(self.srch_inc - c.srch_inc) +\
               abs(self.min_len - c.min_len) + abs(self.max_len - c.max_len)



class ConstraintType:
    def __init__(self, name, init_function):
        self.name = name
        self.current_vals = []
        self.priors = []
        self.posteriors = []
        init_function(self)


def init_func_closure(assgn_cvs: list[int], assgn_priors: list[float], assgn_posts: list[float]):

    def init_func(constraint_type):
        constraint_type.current_vals = copy.deepcopy(assgn_cvs)
        constraint_type.priors = copy.deepcopy(assgn_priors)
        constraint_type.postseriors = copy.deepcopy(assgn_posts)

    return init_func


ct_name_to_init_map = {
    "max_diff": init_func_closure([1], [1.0], [1.0]),
    "tot_diff": init_func_closure([1], [1.0], [1.0]),
    "nxt_inc": init_func_closure([1], [1.0], [1.0]),
    "srch_inc": init_func_closure([1], [1.0], [1.0]),
    "min_len": init_func_closure([1], [1.0], [1.0]),
    "max_len": init_func_closure([5], [1.0], [1.0]),

}

def init_constraint_types():
    constraint_names = []
    constraint_types = [ConstraintType(name, ifunc) for name, ifunc in ct_name_to_init_map]
    return constraint_types 






