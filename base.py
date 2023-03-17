import brains
import world
import hexcoords


class Base(world.Entity):
    def __init__(self, pos: hexcoords.Position,
                 direction: hexcoords.Direction,
                 team,
                 spawn_function: callable([world.Entity, brains.SpawnData]),
                 brain: brains.BaseBrain,
                 stop_function: callable([]),
                 get_unit_count: callable([[],int])
                 ):
        super().__init__(pos, direction, team)
        self.world = world
        self.ticks = 0
        self.energy = 420
        self.spawn_cooldown = 0
        self.spawn_function = spawn_function
        self.brain = brain
        self.stop_function = stop_function
        self.get_unit_count = get_unit_count
        self.spawns: list[brains.SpawnData | None] = [None, None, None, None, None, None]

    def end_round(self):
        self.brain.round_end(self.ticks,self.energy)
        self.energy = 420
        self.ticks = 0
        self.spawn_cooldown = 0

    def spawn_unit(self, direction):
        self.spawn_function(self.pos + direction.vector(), direction, 0)

    def evaluate(self, world_map, pheros, enemies, friends):
        self.ticks = self.ticks + 1
        self.energy = min(self.energy+42-3*self.get_unit_count(), 420)
        try:
            self.spawns = self.brain.evaluate(self.ticks, self.energy)
            if len(self.spawns) != 6:
                raise
        except:
            self.spawns = [None,None,None,None,None,None]

    def act(self):
        if self.spawn_cooldown != 0:
            self.spawn_cooldown -= 1
            return
        if sum(x is not None for x in self.spawns) * 42 <= self.energy:
            self.spawn_cooldown += 42
            for idx, spawn in enumerate(self.spawns):
                if spawn is not None:
                    self.energy -= 42
                    self.spawn_unit(self.direction+hexcoords.DIRECTION_STEP*idx)

    def mov(self):
        pass

    def dmg(self, value):
        self.energy -= value
        if self.energy < 0:
            self.destroy()

    def destroy(self):
        print("player " + self.team, " lost the game")
        self.stop_function(self.team)
