# Imports:
import math
from food import Food
from constants import *

class Agent:
    """
    A class used to represent an Agent

    Attributes
    ----------
    kind : str
        Agent's kind
    food_types : list
        Food the agent eats
    fov_angle : int
        Agent's FOV angle
    fov_distance : int
        Aagent's FOV distance
    energy : float
        Agent's initial energy
    speed : float
        Agent's speed
    angle : float
        Agent's angle
    alive : bool
        Whether the agent is alive or not
    x : float
        Agent's x position
    y : float
        Agent's y position

    Methods
    -------
    calculate_angle_to_object(self, curr_object)
        Calculating the agent's angle to the given object
    is_in_fov(self, angle_to_object, curr_object)
        Checking whether an object is in the agent's FOV
    """

    def __init__(self, kind, food_types) -> None:
        """
        Parameters
        ----------
        kind : str
            Agent's kind
        food_types : list
            Food the agent eats
        """

        # Agent user defined properties:
        self.kind = kind
        self.food_types = food_types
        self.fov_angle = 30
        self.fov_distance = 10
        self.energy = INITIAL_ENERGY
        self.speed = INITIAL_SPEED
        
        # Agent regular properties: 
        self.angle = 0
        self.alive = True
        self.x = 0
        self.y = 0

    
    def calculate_angle_to_object(self, curr_object):
        """
        Calculating the agent's angle to the given object

        Parameters
        ----------
        curr_object : Food / Agent
            Given object
        
        Returns
        -------
        float
            Angle to the given object
        """
        return math.degrees(math.atan2((curr_object.y - self.y), (curr_object.x - self.x)))

    def is_in_fov(self, angle_to_object, curr_object):
        """
        Checking whether an object is in the agent's FOV

        Parameters
        ----------
        angle_to_object : float
            Agent's angle to the food
        curr_object : Food / Agent
            Given object
        
        Returns
        -------
        bool
            True  - the given object is in the agent's FOV
            False - otherwise
        """
        return abs(math.atan2(math.sin(math.radians(angle_to_object - self.angle)), math.cos(math.radians(angle_to_object - self.angle)))) < math.radians(self.fov_angle) / 2 and \
                math.dist([curr_object.x, curr_object.y], [self.x, self.y]) < self.fov_distance