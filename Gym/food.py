# Imports:
from constants import *

class Food:
    """
    A class used to represent Food

    Attributes
    ----------
    kind : str
        Food's kind
    food_energy : float
        Energy the food gives when eaten
    alive : bool
        Always true
    x : float
        Food's x position
    y : float
        Food's y position
    """

    def __init__(self, kind) -> None:
        """
        Parameters
        ----------
        kind : str
            Food's kind
        """

        # Food properties:
        self.kind = kind
        self.food_energy = FOOD_ENERGY
        self.alive = True
        self.x = 0
        self.y = 0