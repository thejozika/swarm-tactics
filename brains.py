import random
from enum import IntEnum, auto
import nptyping
import numpy as np


class SpawnData:
    def __init__(self, data, brain, **kwargs):
        self.data = data
        self.brain = brain()


# Contains the Vision Sensors starting with left behind to Behind over the Front.
# 0 means nothing can be seen/or no eye avaiable
# positive values mean neutral or friend
# negative values mean enemy
# The absolute amount is the distance (closer means higher)
ViewData = nptyping.NDArray[nptyping.Shape["6"], nptyping.Float]


# Contains the Sensor Data starting with left behind to behind over the Front.
# 0 Means Base, a positive value gives unit value (no Team)s
# a negative Value means Environment, or not connected Sensor
SensorData = nptyping.NDArray[nptyping.Shape["6,2"], nptyping.Float]


# Contains The Pheromon Data starting with left behind to behind over the Front.
# Data is stored as Tensor with respective Dimensions R,G,B
# 0 means no pheromones or no sensor avaiable. Is non negative.
PheromoneData = nptyping.NDArray[nptyping.Shape["6,2,3"], nptyping.Float]




class BaseBrain:
    def evaluate(self, age, energy) -> (
            SpawnData, SpawnData, SpawnData, SpawnData, SpawnData, SpawnData):
        return [None, None, None, None, None, None]

    def round_end(self,age,energy):
        pass


class Movement(IntEnum):
    NOP = auto()
    MOVE = auto()
    TL = auto()
    TR = auto()


class Action(IntEnum):
    NOP = auto()
    ATTACK = auto()
    REMOVE_PHEROMON = auto()
    EMIT_PHEROMON = auto()
    SCREAM_R = auto()
    SCREAM_G = auto()
    SCREAM_B = auto()


class Input():
    def __init__(self):
        pass


class UnitBrain:
    def evaluate(self, age, energy, vision:ViewData, sense:SensorData, smell:PheromoneData) \
            -> (Movement, Action):
        return Movement.NOP,Action.NOP
