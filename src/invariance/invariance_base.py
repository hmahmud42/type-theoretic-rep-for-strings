from types import MethodType
from typing import Callable, Any
from invariance_core import ConcInv, ActivecConcInvWrapper


class ConcInvarianceBase(ConcInv):
    def __init__(self, value: Any, loc, diff_func: Callable[[Any, Any], float]):
        self.level = 0
        self.value = value
        self.loc = loc
        self.tup_value = tuple(value)
        self.diff_func = MethodType(diff_func, self)

        self.params = {"value": value, loc: "loc"}
        self.args = {"arg_1": {"ind_type": "tuple", 
                              "elem_type": "int", 
                              "len": len(value)}}
        self.ret_type = {"ret_type": "Int"}

    def get_types(self):
        """
        Returns the types of the arguments this thing accepts and returns,
        This includes sad versions of dependent types (specifically 
        Sigma types)
        """
        return (self.params, self.args, self.ret_type)

    def create_active(self, args):
        """
        Calculates the degree to which the invariance is satisfied
        """
        return ActivecConcInvWrapper(
                self,
                {
                    "isequal": self.value == args,
                },
            )

    
