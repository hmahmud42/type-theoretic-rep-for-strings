from abc import ABC, abstractmethod


class ConcInv(ABC):
    """
    Class representing a invariance function 
    """
    @abstractmethod 
    def get_types(self):
        """
        Returns the types of the arguments this thing accepts and returns,
        This includes sad versions of dependent types (specifically 
        Sigma types)
        """
        pass

    @abstractmethod
    def create_active(self, args):
        """
        Calculates the degree to which the invariance is satisfied
        """
        pass


class ActivecConcInvWrapper:
    """
    Class wrapping an active instance of a concrete invariance.
    """
    def __init__(self, conc_inv, output_value):
        self.conc_inv = conc_inv
        self.output_value = output_value


