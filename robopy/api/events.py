from robopy.api.objects import Bullet


class Event:
    def __init__(self, time: int):
        self.time: int = time


class BulletHitEvent(Event):
    def __init__(self, time: int, name: str, energy: float, bullet: Bullet):
        super().__init__(time)

        self.name: str = name
        self.energy: float = energy
        self.bullet: Bullet = bullet


class BulletHitBulletEvent(Event):
    def __init__(self, time: int, bullet: Bullet, hit_bullet: Bullet):
        super().__init__(time)

        self.bullet: Bullet = bullet
        self.hit_bullet: Bullet = hit_bullet


class BulletMissedEvent(Event):
    def __init__(self, time: int, bullet: Bullet):
        super().__init__(time)

        self.bullet = bullet


class DeathEvent(Event):
    def __init__(self, time: int):
        super().__init__(time)


class CustomEvent(Event):
    def __init__(self, time: int, name: str):
        super().__init__(time)

        self.name = name


class HitByBulletEvent(Event):
    def __init__(self, time: int, bearing: float, bullet: Bullet):
        super().__init__(time)

        self.bearing: float = bearing
        self.bullet: Bullet = bullet


class HitRobotEvent(Event):
    def __init__(self, time: int, name: str, energy: float, bearing: float, guilty: bool):
        super().__init__(time)

        self.name: str = name
        self.energy: float = energy
        self.bearing: float = bearing
        self.guilty: bool = guilty


class HitWallEvent(Event):
    def __init__(self, time: int, bearing: float):
        super().__init__(time)

        self.bearing: float = bearing


class RobotDeathEvent(Event):
    def __init__(self, time: int, name: str):
        super().__init__(time)

        self.name: str = name


class ScannedRobotEvent(Event):
    def __init__(self, time: int, name: str, heading: float, energy: float, velocity: float, bearing: float, distance: float):
        super().__init__(time)

        self.name: str = name
        self.heading: float = heading
        self.energy: float = energy
        self.velocity: float = velocity
        self.bearing: float = bearing
        self.distance: float = distance


class SkippedTurnEvent(Event):
    def __init__(self, time: int, turn: int):
        super().__init__(time)

        self.turn: int = turn


class StatusEvent(Event):
    def __init__(self, time: int, status: dict):
        super().__init__(time)

        self.status: dict = status


class VictoryEvent(Event):
    def __init__(self, time: int):
        super().__init__(time)
