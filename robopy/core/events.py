import enum


@enum.unique
class EventKind(enum.IntEnum):
    #: TODO how to typify enum?
    BulletHit = enum.auto()
    BulletHitBullet = enum.auto()
    BulletMissed = enum.auto()
    Death = enum.auto()
    Custom = enum.auto()
    HitByBullet = enum.auto()
    HitRobot = enum.auto()
    HitWall = enum.auto()
    RobotDeath = enum.auto()
    ScannedRobot = enum.auto()
    SkippedTurn = enum.auto()
    Status = enum.auto()
    Victory = enum.auto()


class EventCore:
    def __init__(self, time: int, kind, args: tuple):
        self.time: int = time
        self.kind = kind  #: TODO how to typify enum?
        self.args: tuple = args

    def __lt__(self, other: 'EventCore'):
        return (self.time, other.critical, other.priority) < (other.time, self.critical, self.priority)

    @property
    def critical(self) -> bool:
        if self.kind is EventKind.BulletHit:
            return False
        elif self.kind is EventKind.BulletHitBullet:
            return False
        elif self.kind is EventKind.BulletMissed:
            return False
        elif self.kind is EventKind.Death:
            return True
        elif self.kind is EventKind.Custom:
            return True
        elif self.kind is EventKind.HitByBullet:
            return False
        elif self.kind is EventKind.HitRobot:
            return False
        elif self.kind is EventKind.HitWall:
            return False
        elif self.kind is EventKind.RobotDeath:
            return False
        elif self.kind is EventKind.ScannedRobot:
            return False
        elif self.kind is EventKind.SkippedTurn:
            return True
        elif self.kind is EventKind.Status:
            return False
        elif self.kind is EventKind.Victory:
            return True
        else:
            raise Exception("unknown event kind")

    @property
    def priority(self) -> int:
        if self.kind is EventKind.BulletHit:
            return 50
        elif self.kind is EventKind.BulletHitBullet:
            return 55
        elif self.kind is EventKind.BulletMissed:
            return 60
        elif self.kind is EventKind.Death:
            return -1
        elif self.kind is EventKind.Custom:
            return 80
        elif self.kind is EventKind.HitByBullet:
            return 20
        elif self.kind is EventKind.HitRobot:
            return 40
        elif self.kind is EventKind.HitWall:
            return 30
        elif self.kind is EventKind.RobotDeath:
            return 70
        elif self.kind is EventKind.ScannedRobot:
            return 10
        elif self.kind is EventKind.SkippedTurn:
            return 100
        elif self.kind is EventKind.Status:
            return 99
        elif self.kind is EventKind.Victory:
            return 100
        else:
            raise Exception("unknown event kind")
