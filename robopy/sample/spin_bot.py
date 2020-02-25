import math

import robopy.api.events as events
from robopy.api.robot import Robot


class SpinBot(Robot):

    def _run(self):
        #: Loop forever.
        while True:
            #: Tell the game that when we take move,
            #: we'll also want to turn right... a lot.
            self.turn(math.radians(10000))
            #: Limit our speed to 5
            self.set_max_velocity(5)
            #: Start moving (and turning).
            self.move(10000, execute=True)
            #: Repeat.

    def handle_hit_robot(self, e: events.HitRobotEvent):
        if -math.radians(10) < e.bearing < math.radians(10):
            self.fire(3, execute=True)
        if e.guilty:
            self.turn(math.radians(10))

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        self.fire(3, execute=True)
