
def int_hamming(l1: list[int], l2: list[int]) -> int:
    v = 0
    for a, b in zip(l1, l2):
        v += int(a !=b )
    return v


def base_inv_diff(self, bp):
    """
    Hamming distance between different base pattern based on the tuple values.
    """
    return int_hamming(self.value, bp.value)