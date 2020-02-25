import math

import robopy.api.events as events
from robopy.api.robot import Robot


class Walls(Robot):
    def __init__(self, wrapper):
        super().__init__(wrapper)

        #: Initialize move_amount to the maximum possible for this battlefield.
        self.move_amount: int = max(self.battlefield.height, self.battlefield.width)
        #: Initialize peek to false.
        self.peek: bool = False

    def _run(self):
        #: Turn left to face a wall.
        #: self.heading % math.radians(90) means the remainder of
        #: self.heading divided by math.radians(90).
        self.turn(-(self.heading % math.radians(90)), execute=True)
        self.move(self.move_amount, execute=True)

        #: Turn the gun to turn right 90 degrees.
        self.peek = True
        self.turn_gun(math.radians(90), execute=True)
        self.turn(math.radians(90), execute=True)

        while True:
            #: Look before we turn when self.move() completes.
            self.peek = True
            #: Move up the wall.
            self.move(self.move_amount, execute=True)
            #: Don't look now.
            self.peek = False
            #: Turn to the next wall.
            self.turn(math.radians(90), execute=True)

    def handle_hit_robot(self, e: events.HitRobotEvent):
        if -math.radians(90) < e.bearing < math.radians(90):
            #: He's in front of us, set back up a bit.
            self.move(-100, execute=True)
        else:
            #: He's in back of us, so set ahead a bit.
            self.move(100, execute=True)

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        self.fire(2, execute=True)
        #: Note that scan is called automatically when the robot is moving.
        #: By calling it manually here, we make sure we generate another scan event if there's a robot on the next
        #: wall, so that we do not start moving up it until it's gone.
        if self.peek:
            self.scan(execute=True)
