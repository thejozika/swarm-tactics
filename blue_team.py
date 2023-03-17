import random

import brains
from brains import Movement, Action, SpawnData, ViewData, SensorData, PheromoneData


class BaseBrain(brains.BaseBrain):
    pass
    def evaluate(self, age, energy) -> (
            SpawnData, SpawnData, SpawnData, SpawnData, SpawnData, SpawnData):
        if energy >= 200:
            return [SpawnData(data=0, brain=UnitBrain), SpawnData(data=0, brain=UnitBrain), None, None, None,
                    SpawnData(data=0, brain=UnitBrain)]


class UnitBrain(brains.UnitBrain):
    def __init__(self):
        self.movs = random.randint(10, 30)
        if random.randint(0, 2) == 0:
            self.defaultDir = Movement.TL
            self.otherDir = Movement.TR
        else:
            self.defaultDir = Movement.TR
            self.otherDir = Movement.TL

    def evaluate(self, age, energy, vision: ViewData, sense: SensorData, smell: PheromoneData) -> (Movement, Action):
        front_left = vision[1]
        front = vision[2]
        front_right = vision[3]
        if energy < 11:
            return Movement.NOP,Action.NOP
        if front == -1:
            return Movement.NOP, Action.ATTACK
        if front < 0:
            return Movement.MOVE, Action.EMIT_PHEROMON
        if front_left < 0:
            return Movement.TL, Action.EMIT_PHEROMON
        if front_right < 0:
            return Movement.TR, Action.EMIT_PHEROMON
        if energy <21:
            return Movement.NOP, Action.NOP
        max = 0
        maxidx = None
        for idx,dir in enumerate(smell):
            for val in dir:
                if val[2] > max:
                    max = val[2]
                    maxidx = idx
        if maxidx is not None and (maxidx == 0 or maxidx == 1):
            return Movement.TL, Action.NOP
        if maxidx is not None and maxidx == 2:
            return Movement.MOVE, Action.NOP
        if maxidx is not None and (maxidx == 3 or maxidx == 4):
            return Movement.TR, Action.NOP

        if energy < 35:
            return Movement.NOP, Action.NOP
        if front == 1:
            if front_left == 1 and front_right == 1:
                return self.defaultDir, Action.NOP
            elif front_right == 0 and front_right == 0:
                return self.defaultDir, Action.NOP
            elif front_right == 0 and front_left == 1:
                return Movement.TR, Action.NOP
            else:
                return Movement.TL, Action.NOP
        return Movement.MOVE, Action.NOP
