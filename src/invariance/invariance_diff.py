from invariance_base import ConcInv, ActivecConcInvWrapper


class ConcInvBaseMaxDiffMin(ConcInv):
    """
    Invariance that is a diff over base features for arbitrary
    lengths as long as it is greater than min-length
    """

    def __init__(self, diff_val, min_len):
        self.diff_val = diff_val
        self.min_len = min_len
        self.params = {"min_len": min_len}
        self.args = {"arg_1": {"ind_type": "List", "elem_type": "Base"}}
        self.ret_type = {"ret_type": "Int"}

    def get_types(self):
        return (self.params, self.args, self.ret_type)

    def create_active(self, args):
        root = args[0]
        max_diff = 0
        i = -1
        for i, val in enumerate(args[1:]):
            diff = root.diff(val)
            if diff > self.max_diff:
                break
            max_diff = max(diff, max_diff)

        if i >= 0:
            return ActivecConcInvWrapper(
                self,
                {"len_sub_min_len": i + 1 - self.min_len, 
                 "max_obvs_diff": max_diff},
            )
        else:
            return None


    def type_check(self, type_check_state, args):
        if type_check_state["completed"]: 
            return not type_check_state["failed"]

        if type_check_state["root"].diff(args[-1]) > self.max_diff:
            type_check_state["failed"] = True
            type_check_state["completed"] = True
            return False 
        else:
            type_check_state["failed"] = True
            if type_check_state["len"] > self.max_len:
                type_check_state["completed"] = True



class ConcInvBaseMaxDiffBtwn(ConcInv):
    """
    Invariance that is a diff over base features for lengths between
    min-len and max-len.
    """

    def __init__(self, diff_val, min_len, max_len):
        self.diff_val = diff_val
        self.min_len = min_len
        self.max_len = max_len
        self.rng = (max_len - min_len) / 2

        self.params = {"min_len": min_len, "max_len": max_len}
        self.args = {"arg_1": {"ind_type": "List", "elem_type": "Base"}}
        self.ret_type = {"ret_type": "Int"}

    def get_arg_types(self):
        return (self.params, self.args, self.ret_type)

    def create_active(self, args):
        root = args[0]
        diff_sum = 0
        i = -1
        for i, val in enumerate(args[1:]):
            diff = root.diff(val)
            if diff > self.max_diff or i >= self.max_len:
                break
            diff_sum += diff

        if i >= 0:
            return ActivecConcInvWrapper(
                self,
                {
                    "mid_val": max(i + 1 - self.min_len, self.max_len - i - 1) / self.rng,
                    "mean_obvs_diff": diff_sum / (i + 1),
                },
            )
        else:
            return None


class ConcInvNumericMaxDiffMin(ConcInvBaseMaxDiffMin):
    """
    Invariance that is a diff over numeric values for arbitrary
    lengths as long as it is greater than min-length
    """

    def __init__(self, diff_val, min_len):
        super(ConcInvNumericMaxDiffMin, self)
        self.args = {"arg_1": {"ind_type": "List", "elem_type": "Num"}}

    def create_active(self, args):
        root = args[0]
        max_diff = 0
        i = -1

        for i, val in enumerate(args[1:]):
            diff = abs(root - val)
            if diff > self.max_diff:
                break
            max_diff = max(diff, max_diff)

        if i >= 0:
            return ActivecConcInvWrapper(
                self,
                {"len_sub_min_len": i + 1 - self.min_len, "max_obvs_diff": max_diff},
            )
        else:
            return None


class InvNumericMaxDiffBtwn(ConcInvBaseMaxDiffBtwn):
    """
    Invariance that is a diff over base features for lengths between
    min-len and max-len.
    """

    def __init__(self, diff_val, min_len):
        super(InvNumericMaxDiffBtwn, self)
        self.args = {"arg_1": {"ind_type": "List", "elem_type": "Int"}}

    def create_active(self, args):
        root = args[0]
        diff_sum = 0
        i = -1

        for i, val in enumerate(args[1:]):
            diff = root.diff(val)
            if diff > self.max_diff or i >= self.max_len:
                break
            diff_sum += diff

        if i >=0 0:
            return ActivecConcInvWrapper(
                self,
                {
                    "mid_val": max(i + 1 - self.min_len, self.max_len - i - 1) / self.rng,
                    "mean_obvs_diff": diff_sum / (i + 1),
                },
            )
        else:
            return None





