import itertools

import util
import numpy as np
import hexcoords

from ENV import PHEROMON_GREEN_STATIC_FACTOR, RED, BLUE, PHEROMON_GREEN_SET_FACTOR, PHEROMON_TEAM_SET_FACTOR, \
    PHEROMON_TEAM_STATIC_FACTOR


class Entity:
    def __init__(self, pos: hexcoords.Position, dir: hexcoords.Direction, col):
        self.pos = pos
        self.dir = dir
        self.col = col

    def evaluate(self, world_map, pheros, enemies, friends):
        pass

    def act(self):
        pass

    def mov(self):
        pass

    def dmg(self, value):
        pass

    def destroy(self):
        pass

    def identity(self):
        return 0

    def move_in_direction(self):
        self.pos = self.pos + self.direction.vector()

    def turn_left(self):
        self.dir = self.direction << 1

    def turn_right(self):
        self.dir = self.direction >> 1

    @property
    def position(self) -> hexcoords.Position:
        return self.pos

    @property
    def direction(self) -> hexcoords.Direction:
        return self.dir

    @property
    def team(self):
        return self.col


dt_Entity = np.dtype(Entity)


def red_map(x: Entity):
    if x is not None and x.team == RED:
        return x.identity()
    else:
        return -1


def blue_map(x: Entity):
    if x is not None and x.team == BLUE:
        return x.identity()
    else:
        return -1


vect_red_map = np.vectorize(red_map, [dt_Entity])
vect_blue_map = np.vectorize(blue_map, [dt_Entity])


class World:
    def __init__(self, world_radius, blue_base: Entity, red_base: Entity, empty=False):
        self.world_radius = world_radius
        self.diameter = 2 * world_radius + 1
        if not empty:
            self.world_map = util.map_generator(self.diameter, self.diameter)
        else:
            self.world_map = np.zeros((self.diameter, self.diameter), dtype=int)
        self.positions = []
        self.initialise_world_background()

        for base_vector in hexcoords.ALL_BASES:
            self.world_map[(blue_base.position + base_vector).matrix_coordinates] = 0
            self.world_map[(red_base.position + base_vector).matrix_coordinates] = 0
        self.world_map[blue_base.position.matrix_coordinates] = 0
        self.world_map[red_base.position.matrix_coordinates] = 0
        self.world_map[hexcoords.Position(0, 0, 0).matrix_coordinates] = 1

        self.red_base = red_base
        self.blue_base = blue_base
        self.wall_count = util.get_sourrounding_wall_count_map(self.world_map)

        self.green_pheromon = self.get_0_map()
        self.green_pheromon_old = self.get_0_map()

        self.blue_pheromon = self.get_0_map()
        self.blue_pheromon_old = self.get_0_map()

        self.red_pheromon = self.get_0_map()
        self.red_pheromon_old = self.get_0_map()

        self.unit_map = np.full((self.diameter, self.diameter), None, dt_Entity)
        self.kill_map = self.get_0_map()
        self.dmg_map = self.get_0_map()

        self.hit1 = None
        self.hit2 = None

    @property
    def pheromone(self):
        return self.red_pheromon.copy(), self.green_pheromon.copy(), self.blue_pheromon.copy()

    @property
    def kill_locations(self):
        return self.world_map + self.kill_map

    @property
    def dmg(self):
        return self.dmg_map

    @property
    def red_info(self):
        return vect_red_map(self.unit_map)

    @property
    def blue_info(self):
        return vect_blue_map(self.unit_map)

    def get_0_map(self):
        return np.zeros((self.diameter, self.diameter))

    def initialise_world_background(self):
        for x in range(self.diameter):
            for y in range(self.diameter):
                r = x - self.world_radius
                q = y - self.world_radius
                s = -(r + q)
                try:
                    pos = hexcoords.Position(r, q, s)
                    if pos.metric_length() == self.world_radius:
                        self.world_map[pos.matrix_coordinates] = 1
                    else:
                        self.positions.append(pos)
                except:
                    self.world_map[x, y] = -1

    # update functions, which shall be called in the end
    def update_pheromon(self):
        self.red_pheromon_old = np.array([[0 if lvl < 1 else lvl for lvl in row] for row in self.red_pheromon])
        self.red_pheromon.fill(0)
        self.green_pheromon_old = np.array([[0 if lvl < 1 else lvl for lvl in row] for row in self.green_pheromon])
        self.green_pheromon.fill(0)
        self.blue_pheromon_old = np.array([[0 if lvl < 1 else lvl for lvl in row] for row in self.blue_pheromon])
        self.blue_pheromon.fill(0)

        for pos in self.positions:
            self.green_pheromon[pos.matrix_coordinates] += PHEROMON_GREEN_STATIC_FACTOR * self.green_pheromon_old[
                pos.matrix_coordinates]
            self.red_pheromon[pos.matrix_coordinates] += PHEROMON_TEAM_STATIC_FACTOR * self.red_pheromon_old[
                pos.matrix_coordinates]
            self.blue_pheromon[pos.matrix_coordinates] += PHEROMON_TEAM_STATIC_FACTOR * self.blue_pheromon_old[
                pos.matrix_coordinates]
            wall_count = self.wall_count[pos.matrix_coordinates]
            for base in hexcoords.ALL_BASES:
                if self.world_map[(pos + base).matrix_coordinates] == 0:
                    self.red_pheromon[(pos + base).matrix_coordinates] += (1 - PHEROMON_TEAM_STATIC_FACTOR) * 1 / (
                            6 - wall_count) * self.red_pheromon_old[pos.matrix_coordinates]
                    self.green_pheromon[(pos + base).matrix_coordinates] += (1 - PHEROMON_GREEN_STATIC_FACTOR) * 1 / (
                            6 - wall_count) * self.green_pheromon_old[pos.matrix_coordinates]
                    self.blue_pheromon[(pos + base).matrix_coordinates] += (1 - PHEROMON_TEAM_STATIC_FACTOR) * 1 / (
                            6 - wall_count) * self.blue_pheromon_old[pos.matrix_coordinates]
        self.green_pheromon *= PHEROMON_GREEN_SET_FACTOR
        self.red_pheromon *= PHEROMON_TEAM_SET_FACTOR
        self.blue_pheromon *= PHEROMON_TEAM_SET_FACTOR

    # reset functions, which shall be called after evaluation of the world,to get ready for next cycle
    def reset(self):
        self.red_pheromon = self.get_0_map()
        self.green_pheromon = self.get_0_map()
        self.blue_pheromon = self.get_0_map()

    def reset_maps(self):
        self.unit_map = np.full((self.diameter, self.diameter), None, dt_Entity)
        self.kill_map = self.get_0_map()
        self.dmg_map = self.get_0_map()

    # utility functions, that can be called by entitys
    def emit_red_pheromon(self, pos: hexcoords.Position, value):
        if self.world_map[pos.matrix_coordinates] == 0:
            self.red_pheromon[pos.matrix_coordinates] = min(self.red_pheromon[pos.matrix_coordinates] + value, 255)

    def emit_green_pheromon(self, pos: hexcoords.Position, value):
        if self.world_map[pos.matrix_coordinates] == 0:
            self.green_pheromon[pos.matrix_coordinates] = min(self.green_pheromon[pos.matrix_coordinates] + value, 255)

    def emit_blue_pheromon(self, pos: hexcoords.Position, value):
        if self.world_map[pos.matrix_coordinates] == 0:
            self.blue_pheromon[pos.matrix_coordinates] = min(self.blue_pheromon[pos.matrix_coordinates] + value, 255)

    def remove_red_pheromon(self, pos: hexcoords.Position) -> float:
        val = self.red_pheromon[pos.matrix_coordinates]
        self.red_pheromon[pos.matrix_coordinates] = 0
        return val

    def remove_green_pheromon(self, pos: hexcoords.Position) -> float:
        val = self.green_pheromon[pos.matrix_coordinates]
        self.green_pheromon[pos.matrix_coordinates] = 0
        return val

    def remove_blue_pheromon(self, pos: hexcoords.Position) -> float:
        val = self.blue_pheromon[pos.matrix_coordinates]
        self.blue_pheromon[pos.matrix_coordinates] = 0
        return val

    def kill_at_location(self, pos: hexcoords.Position):
        self.kill_map[pos.matrix_coordinates] = 1
        self.unit_map[pos.matrix_coordinates] = None

    def dmg_at_location(self, pos: hexcoords.Position, value):
        self.dmg_map[pos.matrix_coordinates] += value

    def register_entity(self, ent: Entity):
        if ent is not None and self.unit_map[ent.position.matrix_coordinates] is not None:
            self.kill_map[ent.position.matrix_coordinates] = 1
        elif ent is not None and self.kill_map[ent.position.matrix_coordinates] == 1 or \
                self.world_map[ent.position.matrix_coordinates] == 1:
            return
        else:
            self.unit_map[ent.position.matrix_coordinates] = ent
