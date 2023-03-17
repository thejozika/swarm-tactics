from brains import Action, Movement
import brains
import hexcoords
import world
from sensor_gen import get_sensor_data, get_pheromone_data, get_vision_data
from ENV import UNIT_DAMAGE, RED, BLUE, UNIT_PHERO_EMISSION


class InteractionModel:
    def emit_red_pheromon(self, pos: hexcoords.Position, value):
        pass

    def emit_green_pheromon(self, pos: hexcoords.Position, value):
        pass

    def emit_blue_pheromon(self, pos: hexcoords.Position, value):
        pass

    def kill_at_location(self, pos: hexcoords.Position):
        pass

    def dmg_at_location(self, pos: hexcoords.Position, value):
        pass

    def remove_red_pheromon(self, pos: hexcoords.Position) -> float:
        pass

    def remove_green_pheromon(self, pos: hexcoords.Position) -> float:
        pass

    def remove_blue_pheromon(self, pos: hexcoords.Position) -> float:
        pass


class Unit(world.Entity):
    def __init__(self, pos: hexcoords.Position, direction, team, val, brain: brains.UnitBrain,
                 world_model: InteractionModel, delFunction):
        super().__init__(pos, direction, team)
        self.movement = Movement.NOP
        self.action = Action.NOP
        self.brain = brain
        self.energy = 42
        self.age = 0
        self.world_model = world_model
        self.delFunction = delFunction

    def identity(self):
        return 1

    def evaluate(self, world_map, pheros, enemies, friends):
        if self.energy <= 0:
            self.destroy()
        self.age += 1
        if self.age < 420:
            self.energy = min(42, self.energy + 1)
        if self.age == 450:
            self.destroy()

        vision = get_vision_data(self.position, self.direction, world_map, enemies, friends)
        sense = get_sensor_data(self.position, self.direction, world_map, enemies, friends)
        smell = get_pheromone_data(self.position, self.direction, pheros)

        # try:
        self.movement, self.action = self.brain.evaluate(self.age, self.energy, vision, sense, smell)
        # except:
        #     self.destroy()

    def act(self):
        if self.action == Action.ATTACK:
            self.world_model.dmg_at_location(self.position + self.direction.vector(), UNIT_DAMAGE)
            self.energy -= 10
        elif self.action == Action.EMIT_PHEROMON:
            if self.team == RED:
                self.world_model.emit_red_pheromon(self.position, UNIT_PHERO_EMISSION * 10)
            elif self.team == BLUE:
                self.world_model.emit_blue_pheromon(self.position, UNIT_PHERO_EMISSION * 10)
            self.energy -= 1
        elif self.action == Action.REMOVE_PHEROMON:
            self.energy += self.world_model.remove_green_pheromon(self.position) / UNIT_PHERO_EMISSION
            if self.team == RED:
                self.energy += self.world_model.remove_red_pheromon(self.position) / (100 * UNIT_PHERO_EMISSION)
            elif self.team == BLUE:
                self.energy += self.world_model.remove_blue_pheromon(self.position) / (100 * UNIT_PHERO_EMISSION)
        self.action = Action.NOP

    def mov(self):
        if self.movement == Movement.MOVE:
            self.energy -= 5
            self.world_model.emit_green_pheromon(self.position, 5 * UNIT_PHERO_EMISSION)
            self.move_in_direction()
        elif self.movement == Movement.TL:
            self.energy -= 1
            self.world_model.emit_green_pheromon(self.position, 1 * UNIT_PHERO_EMISSION)
            self.turn_left()
        elif self.movement == Movement.TR:
            self.energy -= 1
            self.world_model.emit_green_pheromon(self.position, 1 * UNIT_PHERO_EMISSION)
            self.turn_right()
        self.movement = Movement.NOP

    def dmg(self, value):
        self.energy -= value
        if self.energy < 0:
            self.destroy()

    def destroy(self):
        self.world_model.emit_green_pheromon(self.pos, max(self.energy, 0) * UNIT_PHERO_EMISSION)
        self.delFunction(self)
