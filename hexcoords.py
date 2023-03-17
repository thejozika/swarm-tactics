from ENV import WORLD_RADIUS


class WorldInformation:
    def __init__(self, default, type, radius):
        self.default = default
        self.type = type
        self.radius = radius


class Position:
    world_radius = WORLD_RADIUS
    @staticmethod
    def set_radius(radius):
        Position.world_radius = radius


    @staticmethod
    def _validate(r, q, s):
        return sum([r, q, s]) == 0 and max([abs(r), abs(q), abs(s)]) <= Position.world_radius

    def __init__(self, r: int, q: int, s: int):
        if self._validate(r, q, s):
            self._r, self._q = r, q
            return
        raise Exception("Invalid Position")

    @property
    def r(self):
        return self._r

    @property
    def q(self):
        return self._q

    @property
    def s(self):
        return -(self._r + self.q)

    @property
    def matrix_coordinates(self):
        return Position.world_radius + self.r, Position.world_radius + self.q

    def metric_length(self):
        return max([abs(self.r), abs(self.q), abs(self.s)])

    def __repr__(self):
        return "(" + str(self.r) + "|" + str(self.q) + "|" + str(self.s) + ")"

    def __add__(self, other):
        try:
            return Position(self._r + other.r, self._q + other.q, self.s + other.s)
        except:
            return self

    def __sub__(self, other):
        try:
            return Position(self._r - other.r, self._q - other.q, self.s - other.s)
        except:
            return self

    def __mul__(self, other):
        try:
            return Position(int(self._r * other), int(self._q * other), int(self.s * other))
        except:
            return self

    def __eq__(self, other):
        return self._r == other.r and self._q == other.q


class Direction:
    def __init__(self, val: int):
        self.value = val

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return str(self.value)

    def __add__(self, other):
        return Direction((self.value + other.value) % 360)

    def __sub__(self, other):
        return Direction((self.value - other.value) % 360)

    def __mul__(self, other):
        if other is Direction:
            return Direction((self.value * other.value) % 360)
        else:
            return Direction(self.value * other)

    def __truediv__(self, other):
        return self.value / other.value

    def __floordiv__(self, other):
        return self.value // other.value

    def __mod__(self, other):
        raise self.value % other.value

    def __divmod__(self, other):
        quotient, reminder = divmod(self.value, other.value)
        return quotient, Direction(reminder)

    def __pow__(self, other):
        raise NotImplemented

    def __lshift__(self, other):
        return self - DIRECTION_STEP * other

    def __rshift__(self, other):
        return self - DIRECTION_STEP * other

    def vector(self) -> Position:
        if self == DIRECTION_EAST:
            return VECTOR_EAST
        elif self == DIRECTION_EAST:
            return VECTOR_EAST
        elif self == DIRECTION_SOUTH_EAST:
            return VECTOR_SOUTH_EAST
        elif self == DIRECTION_SOUTH_WEST:
            return VECTOR_SOUTH_WEST
        elif self == DIRECTION_WEST:
            return VECTOR_WEST
        elif self == DIRECTION_NORTH_WEST:
            return VECTOR_NORTH_WEST
        elif self == DIRECTION_NORTH_EAST:
            return VECTOR_NORTH_EAST
        return Position(0, 0, 0)


DIRECTION_EAST = Direction(0)
DIRECTION_SOUTH_EAST = Direction(60)
DIRECTION_SOUTH_WEST = Direction(120)
DIRECTION_WEST = Direction(180)
DIRECTION_NORTH_WEST = Direction(240)
DIRECTION_NORTH_EAST = Direction(300)

DIRECTION_STEP = Direction(60)

VECTOR_EAST = Position(0, 1, -1)
VECTOR_SOUTH_EAST = Position(1, 0, -1)
VECTOR_SOUTH_WEST = Position(1, -1, 0)
VECTOR_WEST = Position(0, -1, 1)
VECTOR_NORTH_WEST = Position(-1, 0, 1)
VECTOR_NORTH_EAST = Position(-1, 1, 0)

ALL_BASES = [VECTOR_EAST, VECTOR_SOUTH_EAST, VECTOR_SOUTH_WEST, VECTOR_WEST, VECTOR_NORTH_WEST, VECTOR_NORTH_EAST]
