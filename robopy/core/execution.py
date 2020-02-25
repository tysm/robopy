import enum
from typing import Callable, Dict, Union

import robopy.core.rules as rules


class Statistics:
    def __init__(self, robots: int):
        self.time: int = 0
        self.battle_state = None  #: TODO how to typify enum?

        self.robots: int = robots
        self.alive_robots: int = robots

    def tick(self):
        self.time += 1


class Command:
    def __init__(self):
        self.move: float = 0.0
        self.turn: float = 0.0
        self.turn_gun: float = 0.0
        self.turn_radar: float = 0.0
        self.fire: float = 0.0
        self.scan: bool = False

        self.max_velocity: float = rules.MAX_VELOCITY
        self.max_turn_rate: float = rules.MAX_TURN_RATE

        self.lock_gun_body: bool = True
        self.lock_radar_gun: bool = True
        self.lock_radar_body: bool = True

        self.wait: Union[Callable[[], bool], None] = None

    @property
    def status(self) -> Dict[str, float]:
        command_status = dict(
            move=self.move,
            turn=self.turn,
            turn_gun=self.turn_gun,
            turn_radar=self.turn_radar,
            fire=self.fire,
            scan=self.scan,
            max_velocity=self.max_velocity,
            max_turn_rate=self.max_turn_rate,
            lock_gun_body=self.lock_gun_body,
            lock_radar_gun=self.lock_radar_gun,
            lock_radar_body=self.lock_radar_body,
            wait=self.wait
        )
        return command_status


@enum.unique
class BattleState(enum.IntEnum):
    #: TODO how to typify enum?
    ENDED = enum.auto()
    RUNNING = enum.auto()
    STOPPED = enum.auto()


@enum.unique
class BulletState(enum.IntEnum):
    #: TODO how to typify enum?
    FIRED = enum.auto()
    MOVING = enum.auto()
    HIT_VICTIM = enum.auto()
    HIT_BULLET = enum.auto()
    HIT_WALL = enum.auto()
    # EXPLODED = enum.auto()
    INACTIVE = enum.auto()


@enum.unique
class RobotState(enum.IntEnum):
    #: TODO how to typify enum?
    ACTIVE = enum.auto()
    HIT_WALL = enum.auto()
    HIT_ROBOT = enum.auto()
    DEAD = enum.auto()


class InterruptedExecutionException(Exception):
    pass
