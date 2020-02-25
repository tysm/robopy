import math

import robopy.api.events as events
from robopy.api.robot import Robot
from robopy.utils.normalization import normalize_angle


class TrackFire(Robot):

    def _run(self):
        #: Loop forever.
        while True:
            self.turn_gun(math.radians(10), execute=True)  #: Scans automatically.

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        #: Calculate exact location of the robot.
        absolute_bearing = self.heading + e.bearing
        bearing_from_gun = math.degrees(normalize_angle(absolute_bearing - self.gun_heading, relative=True))

        if bearing_from_gun <= 3:
            #: It's close enough, fire!
            self.turn_gun(math.radians(bearing_from_gun), execute=True)
            #: We check gun heat here, because executing self.fire
            #: uses a turn, which could cause us to lose track
            #: of the other robot.
            if self.gun_heat == 0:
                self.fire(min(3 - abs(bearing_from_gun), self.energy - 0.1))
        else:
            #: Otherwise just set the gun to turn.
            #: Note: This will have no effect until we call self.scan
            self.turn_gun(math.radians(bearing_from_gun), execute=True)
        #: Generates another scan event if we see a robot.
        #: We only need to call this if the gun (and therefore radar)
        #: are not turning. Otherwise, scan is called automatically.
        if bearing_from_gun == 0:
            self.scan(execute=True)

    def handle_victory(self, e: events.VictoryEvent):
        #: Victory dance.
        self.turn(math.radians(36000))
