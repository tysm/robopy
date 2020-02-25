import math

import robopy.api.events as events
from robopy.api.robot import Robot


class Crazy(Robot):
    def __init__(self, wrapper):
        super().__init__(wrapper)

        self.moving_forward: bool = False

    def _run(self):
        def turn_complete_condition() -> bool:
            return self.status["action_status"]["turn"] == 0.0

        #: Loop forever.
        while True:
            #: Tell the game we will want to move ahead 40000 -- some large number.
            self.move(40000)
            self.moving_forward = True
            #: Tell the game we will want to turn right 90 degrees.
            self.turn(math.radians(90))
            #: At this point, we have indicated to the game that *when we do something*,
            #: we will want to move ahead and turn right.
            #: It is important to realize we have not done anything yet!
            #: In order to actually move, we'll want to call a method that
            #: takes real time, such as self.wait.
            #: self.wait actually starts the action -- we start moving and turning.
            #: It will not return until we have finished turning.
            self.wait(turn_complete_condition)

            #: Note: We are still moving ahead now, but the turn is complete.
            #: Now we'll turn the other way...
            self.turn(-math.radians(180))
            #: ... and wait for the turn to finish ...
            self.wait(turn_complete_condition)
            #: ... then the other way ...
            self.turn(math.radians(180))
            #: ... and wait for that turn to finish.
            self.wait(turn_complete_condition)
            #: Then back to the top to do it all again.

    def reverse_direction(self):
        if self.moving_forward:
            self.move(-40000)
            self.moving_forward = False
        else:
            self.move(40000)
            self.moving_forward = True

    def handle_hit_robot(self, e: events.HitRobotEvent):
        #: If we're moving the other robot, reverse!
        if e.guilty:
            self.reverse_direction()

    def handle_hit_wall(self, e: events.HitWallEvent):
        #: Bounce off!
        self.reverse_direction()

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        self.fire(1, execute=True)
