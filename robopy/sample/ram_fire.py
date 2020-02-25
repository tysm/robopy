import math

import robopy.api.events as events
from robopy.api.robot import Robot


class RamFire(Robot):
    def __init__(self, wrapper):
        super().__init__(wrapper)

        self.turn_direction: int = 1  #: Clockwise or counterclockwise.

    def _run(self):
        #: Spin the gun around slowly... forever.
        while True:
            self.turn(math.radians(5 * self.turn_direction), execute=True)

    def handle_hit_robot(self, e: events.HitRobotEvent):
        if e.bearing >= 0:
            self.turn_direction = 1
        else:
            self.turn_direction = -1
        self.turn(e.bearing, execute=True)

        #: Determine a shot that won't kill the robot...
        #: We want to ram him instead for bonus points.
        if e.energy > 16:
            self.fire(3, execute=True)
        elif e.energy > 10:
            self.fire(2, execute=True)
        elif e.energy > 4:
            self.fire(1, execute=True)
        elif e.energy > 2:
            self.fire(0.5, execute=True)
        elif e.energy > 0.4:
            self.fire(0.1, execute=True)
        self.move(40)  #: Ram him again!

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        if e.bearing >= 0:
            self.turn_direction = 1
        else:
            self.turn_direction = -1

        self.turn(e.bearing, execute=True)
        self.move(e.distance + 5, execute=True)
        self.scan(execute=True)  #: Might want to move ahead again!
