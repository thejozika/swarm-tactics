import hexcoords
import sensor_gen
import world
from ENV import BLUE, RED
from main import Save


class Tutorial1:
    def __init__(self):
        hexcoords.Position.set_radius(5)
        self.runing = True
        self.red_units: set[world.Entity] = set()
        self.blue_units: set[world.Entity] = set()
        self.blue_base = world.Entity(
            hexcoords.Position(0, 0, 0),
            hexcoords.DIRECTION_EAST,
            BLUE
        )
        self.world = world.World(5,
                                 self.blue_base,
                                 world.Entity(pos=hexcoords.Position(0, 0, 0), dir=hexcoords.DIRECTION_EAST, col=RED),
                                 empty=True)
        self.save = Save(self.world.world_map, [self.blue_base], folder="tutorial", filename="tutorial1")
        self.ticks = 0
        self.world_map = self.world.world_map
        self.pheros = self.world.pheromone
        self.red_unit_map = self.world.red_info
        self.blue_unit_map = self.world.blue_info

        self.save.add_step(self.red_units, *self.pheros)
        self.save.add_step(self.red_units, *self.pheros)
        self.save.add_step(self.red_units, *self.pheros)
        self.save.dump()


Tutorial1()


def mock_val():
    return 1


class Tutorial2():
    def __init__(self):
        hexcoords.Position.set_radius(5)
        self.red_base = world.Entity(pos=hexcoords.Position(0, 2, -2), dir=hexcoords.DIRECTION_WEST, col=RED)
        self.blue_base = world.Entity(pos=hexcoords.Position(0, -2, 2), dir=hexcoords.DIRECTION_EAST, col=BLUE)
        self.unit_main = world.Entity(pos=hexcoords.Position(1, 0, -1), dir=hexcoords.DIRECTION_NORTH_EAST, col=RED)
        self.red_units: set[world.Entity] = set()
        self.red_units.add(self.unit_main)
        self.blue_units: set[world.Entity] = set()
        blue1 = world.Entity(pos=hexcoords.Position(-1, 1, 0), dir=hexcoords.DIRECTION_WEST, col=BLUE)
        blue1.identity = mock_val
        blue2 = world.Entity(pos=hexcoords.Position(-3, 2, 1), dir=hexcoords.DIRECTION_EAST, col=BLUE)
        blue2.identity = mock_val
        self.blue_units.add(blue1)
        self.blue_units.add(blue2)
        self.world = world.World(5,
                                 world.Entity(pos=hexcoords.Position(0, 0, 0), dir=hexcoords.DIRECTION_EAST, col=RED),
                                 world.Entity(pos=hexcoords.Position(0, 0, 0), dir=hexcoords.DIRECTION_EAST, col=RED),
                                 empty=True)
        self.world.register_entity(self.red_base)
        self.world.register_entity(self.blue_base)
        self.world.register_entity(blue1)
        self.world.register_entity(blue2)

        self.save = Save(self.world.world_map,
                         [self.red_base, self.blue_base]
                         , folder="tutorial", filename="tutorial2")
        self.ticks = 0
        self.world.emit_green_pheromon(pos=hexcoords.Position(2, 0, -2), value=102)
        self.world.emit_red_pheromon(pos=hexcoords.Position(-1, 3, -2), value=102)
        self.world.emit_blue_pheromon(pos=hexcoords.Position(2, 0, -2), value=102)
        self.world.emit_blue_pheromon(pos=hexcoords.Position(-2, 3, -1), value=204)
        self.world.emit_green_pheromon(pos=hexcoords.Position(-2, 1, 1), value=102)

        self.world_map = self.world.world_map
        self.pheros = self.world.pheromone
        self.red_unit_map = self.world.red_info
        self.blue_unit_map = self.world.blue_info

        self.save_data()
        self.MV()
        self.save_data()
        self.MV()
        self.save_data()
        self.TL()
        self.save_data()
        self.MV()
        self.save_data()
        self.TL()
        self.save_data()
        self.MV()
        self.save_data()
        self.MV()
        self.save_data()
        self.TL()
        self.save_data()
        self.MV()
        self.save_data()
        self.save_data()
        self.save.declare_loser(BLUE)
        self.save.data_out = True
        self.save.dump()

    def TL(self):
        self.unit_main.turn_left()

    def TR(self):
        self.unit_main.turn_right()

    def MV(self):
        self.unit_main.move_in_direction()

    def save_data(self):
        self.save.add_step(self.red_units.union(self.blue_units), *self.pheros,
                           vision=sensor_gen.get_vision_data(
                           self.unit_main.position,
                           self.unit_main.direction,
                           self.world_map,
                           self.blue_unit_map,
                           self.red_unit_map
                           ),
                           smell=sensor_gen.get_pheromone_data(
                               self.unit_main.position,
                               self.unit_main.direction,
                               self.pheros
                           ),
                           sensor=sensor_gen.get_sensor_data(
                               self.unit_main.position,
                               self.unit_main.direction,
                               self.world_map,
                               self.blue_unit_map,
                               self.red_unit_map
                           ))

Tutorial2()
