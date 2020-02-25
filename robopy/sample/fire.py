import math

import robopy.api.events as events
from robopy.api.robot import Robot
from robopy.utils.normalization import normalize_angle


class Fire(Robot):
    def __init__(self, wrapper):
        super().__init__(wrapper)

        self.dist: int = 50

    def _run(self):
        #: Spin the gun around slowly... forever.
        while True:
            self.turn_gun(math.radians(5), execute=True)

    def handle_hit_by_bullet(self, e: events.HitByBulletEvent):
        self.turn(normalize_angle(math.radians(90) - (self.heading - e.bullet.heading), relative=True), execute=True)

        self.move(self.dist, execute=True)
        self.dist *= -1
        self.scan(execute=True)

    def handle_hit_robot(self, e: events.HitRobotEvent):
        turn_gun_amt = normalize_angle(e.bearing + self.heading - self.gun_heading, relative=True)

        self.turn_gun(turn_gun_amt, execute=True)
        self.fire(3, execute=True)

    def handle_scanned_robot(self, e: events.ScannedRobotEvent):
        if e.distance < 50 and self.energy > 50:
            #: The other robot is close by, and we have plenty of life,
            #: fire hard!
            self.fire(3, execute=True)
        else:
            #: Otherwise, fire 1.
            self.fire(1, execute=True)
        #: Call scan again, before we turn the gun.
        self.scan(execute=True)
