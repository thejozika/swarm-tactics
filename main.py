import itertools
import json

import base
import red_team
import blue_team
import hexcoords
import unit
from ENV import *
import world

BLUE_BASE_POSITION = hexcoords.Position(0, 2 - WORLD_RADIUS, WORLD_RADIUS - 2)
RED_BASE_POSITION = hexcoords.Position(0, WORLD_RADIUS - 2, 2 - WORLD_RADIUS)


class Save:
    def __init__(self, world_map, bases, folder="data", filename="game42"):
        self.world = world_map.tolist()
        self.bases = list(map(self.map_units, bases))
        self.units = []
        self.phero = []
        self.winner = ""
        self.folder = "./" + folder + "/"
        self.filename = filename
        self.data_out = False
        self.sensor = []
        self.vision = []
        self.smell = []

    @staticmethod
    def map_units(entity: world.Entity):
        return *(entity.pos.matrix_coordinates), entity.team, entity.direction / hexcoords.DIRECTION_STEP

    def add_step(self, units: set[world.Entity], phero_r, phero_g, phero_b,vision=None,sensor=None,smell=None):
        self.units.append(list(map(self.map_units, units)))
        self.phero.append([phero_r.tolist(), phero_g.tolist(), phero_b.tolist()])
        if vision is not None:
            self.vision.append(vision.tolist())
        if sensor is not None:
            self.sensor.append(sensor.tolist())
        if smell is not None:
            self.smell.append(smell.tolist())

    def declare_loser(self, team):
        if team == RED:
            self.winner = BLUE
        if team == BLUE:
            self.winner = RED

    def dump(self):
        with open(self.folder + self.filename + ".json" , 'w') as f:
            f.write(json.dumps(self, default=lambda o: o.__dict__))
        with open(self.folder + "rounds.txt", 'a') as f:
            f.write(self.filename + "\n")


class Game:
    def __init__(self, name, rounds):
        self.name = name
        self.runing = True
        self.rounds = rounds
        self.red_units: set[world.Entity] = set()
        self.blue_units: set[world.Entity] = set()
        self.removable: set[world.Entity] = set()
        self.red_base = base.Base(
            RED_BASE_POSITION,
            hexcoords.DIRECTION_WEST,
            RED,
            self.spawn_red_unit,
            red_team.BaseBrain(),
            self.stop,
            lambda: len(self.red_units)
        )
        self.blue_base = base.Base(
            BLUE_BASE_POSITION,
            hexcoords.DIRECTION_EAST,
            BLUE,
            self.spawn_blue_unit,
            blue_team.BaseBrain(),
            self.stop,
            lambda: len(self.blue_units)
        )
        self.world = world.World(WORLD_RADIUS, self.blue_base, self.red_base)

        self.ticks = 0
        self.round = round
        self.world_map = self.world.world_map
        self.pheros = self.world.pheromone
        self.red_unit_map = self.world.red_info
        self.blue_unit_map = self.world.blue_info

    def reset(self):
        self.world.reset()
        self.world.reset_maps()
        self.ticks = 0
        self.red_units.clear()
        self.blue_units.clear()
        self.blue_base.end_round()
        self.red_base.end_round()
        self.runing = True

    def spawn_red_unit(self, position: hexcoords.Position, direction: hexcoords.Direction, val):
        self.red_units.add(self.spawn_unit(position, direction, RED, val, red_team.UnitBrain()))

    def spawn_blue_unit(self, position: hexcoords.Position, direction: hexcoords.Direction, val):
        self.blue_units.add(self.spawn_unit(position, direction, BLUE, val, blue_team.UnitBrain()))

    def spawn_unit(self, position: hexcoords.Position, direction: hexcoords.Direction, team, val, brain):
        return unit.Unit(position, direction, team, val, brain, self.world, self.removal_function)

    def stop(self,team):
        self.save.declare_loser(team)
        self.runing = False

    def removal_function(self, other):
        self.removable.add(other)

    def update(self):
        self.red_unit_map = self.world.red_info
        self.blue_unit_map = self.world.blue_info
        self.evaluate()
        self.world.reset_maps()

        for u in itertools.chain(*[self.red_units, self.blue_units, [self.red_base, self.blue_base]]):
            u.act()
        self.calc_dmg_kill()
        if not self.runing:
            return

        for c in itertools.chain(*[self.red_units, self.blue_units, [self.red_base, self.blue_base]]):
            c.mov()
            self.world.register_entity(c)
        self.calc_dmg_kill()
        self.world.update_pheromon()
        self.pheros = self.world.pheromone
        self.save.add_step(self.red_units.union(self.blue_units),
                           self.pheros[0],
                           self.pheros[1],
                           self.pheros[2])

    def evaluate(self):
        for u in self.red_units:
            u.evaluate(self.world_map, self.pheros, self.blue_unit_map, self.red_unit_map)
        for u in self.blue_units:
            u.evaluate(self.world_map, self.pheros, self.red_unit_map, self.blue_unit_map)
        self.red_base.evaluate(self.world_map, self.pheros, self.blue_unit_map, self.red_unit_map)
        self.blue_base.evaluate(self.world_map, self.pheros, self.red_unit_map, self.blue_unit_map)

    def calc_dmg_kill(self):
        kill_locations = self.world.kill_locations
        dmg = self.world.dmg
        for u in itertools.chain(*[self.red_units, self.blue_units]):
            if kill_locations[u.position.matrix_coordinates] == 1:
                u.destroy()
            else:
                u.dmg(dmg[u.position.matrix_coordinates])
        self.red_base.dmg(dmg[self.red_base.position.matrix_coordinates])
        self.blue_base.dmg(dmg[self.blue_base.position.matrix_coordinates])
        while self.removable:
            u = self.removable.pop()
            self.red_units.discard(u)
            self.blue_units.discard(u)

    def run(self):
        for i in range(self.rounds):
            print("round " + (i+1).__str__() + " started.")
            self.save = Save(self.world_map, [self.red_base, self.blue_base], self.name,
                             "game" + str(i+1))
            while self.runing and self.ticks < MAX_TICKS:
                self.ticks += 1
                if self.ticks % 100 == 0:
                    print("centurie: " + (self.ticks // 100).__str__())
                self.update()
            self.save.dump()
            self.reset()


if __name__ == '__main__':
    open("./data/rounds.txt", 'w').close()
    game = Game("data", ROUNDS)
    game.run()
