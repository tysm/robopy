from typing import List

from robopy.api.objects import Bullet
from robopy.api.events import *  #: TODO name imports.
from robopy.core.events import EventCore, EventKind
from robopy.core.objects import BulletCore
from robopy.utils.threading import List as ThreadingList
from robopy.wrapper.execution import Statistics


def wrapped_args(args_core: tuple) -> tuple:
    args = []
    for arg_core in args_core:
        if isinstance(arg_core, BulletCore):
            args.append(Bullet(arg_core))
        else:
            args.append(arg_core)
    return tuple(args)


class EventManager:
    MAX_EVENT_STACK: int = 2

    def __init__(self, statistics: Statistics, events: 'ThreadingList[EventCore]'):
        self.statistics: Statistics = statistics
        self.events: ThreadingList[EventCore] = events

        self.event_queue: List[EventCore] = []

    @property
    def empty(self) -> bool:
        return len(self.event_queue) == 0

    def consume(self) -> Event:
        event_core = self.event_queue.pop(0)
        time, args = event_core.time, wrapped_args(event_core.args)

        if event_core.kind is EventKind.BulletHit:
            return BulletHitEvent(time, *args)
        elif event_core.kind is EventKind.BulletHitBullet:
            return BulletHitBulletEvent(time, *args)
        elif event_core.kind is EventKind.BulletMissed:
            return BulletMissedEvent(time, *args)
        elif event_core.kind is EventKind.Death:
            return DeathEvent(time, *args)
        elif event_core.kind is EventKind.Custom:
            return CustomEvent(time, *args)
        elif event_core.kind is EventKind.HitByBullet:
            return HitByBulletEvent(time, *args)
        elif event_core.kind is EventKind.HitRobot:
            return HitRobotEvent(time, *args)
        elif event_core.kind is EventKind.HitWall:
            return HitWallEvent(time, *args)
        elif event_core.kind is EventKind.RobotDeath:
            return RobotDeathEvent(time, *args)
        elif event_core.kind is EventKind.ScannedRobot:
            return ScannedRobotEvent(time, *args)
        elif event_core.kind is EventKind.SkippedTurn:
            return SkippedTurnEvent(time, *args)
        elif event_core.kind is EventKind.Status:
            return StatusEvent(time, *args)
        elif event_core.kind is EventKind.Victory:
            return VictoryEvent(time, *args)
        else:
            raise Exception("unknown event kind")

    def process(self):
        with self.events:
            self.event_queue.extend(self.events)
            self.events.clear()

        #: Remove old events.
        self.clear()

        self.event_queue.sort()

    def clear(self):
        time = self.statistics.time
        self.event_queue = [event for event in self.event_queue if time - event.time <= EventManager.MAX_EVENT_STACK]
