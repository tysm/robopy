from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable

from robopy.api import events as events
from robopy.api.objects import Battlefield
from robopy.core.execution import InterruptedExecutionException
from robopy.wrapper.execution import Statistics
from robopy.wrapper.robot import RobotWrapper


class Robot(ABC, Thread):
    def __init__(self, wrapper: RobotWrapper):
        super().__init__(name=f"{wrapper.name}_RobotThread")

        self.__wrapper: RobotWrapper = wrapper
        self.__processing_events: bool = False

    @property
    def battlefield(self) -> Battlefield:
        return self.__wrapper.battlefield

    @property
    def statistics(self) -> Statistics:
        return self.__wrapper.statistics

    @property
    def name(self) -> str:
        return self.__wrapper.name

    @property
    def x(self) -> float:
        return self.__wrapper.x

    @property
    def y(self) -> float:
        return self.__wrapper.y

    @property
    def heading(self) -> float:
        return self.__wrapper.heading

    @property
    def gun_heading(self) -> float:
        return self.__wrapper.gun_heading

    @property
    def radar_heading(self) -> float:
        return self.__wrapper.radar_heading

    @property
    def energy(self) -> float:
        return self.__wrapper.energy

    @property
    def gun_heat(self) -> float:
        return self.__wrapper.gun_heat

    @property
    def velocity(self) -> float:
        return self.__wrapper.velocity

    @property
    def disabled(self) -> bool:
        return self.__wrapper.disabled

    @property
    def status(self) -> dict:
        return self.__wrapper.status

    def run(self):
        try:
            #: Some events such as Status event must occur before the robot has started running.
            #: Thus the robot must process the first events from the first turn.
            self.__process_events()

            self._run()
        except InterruptedExecutionException:
            #: Stops the execution politely.
            pass

    @abstractmethod
    def _run(self):
        pass

    def execute(self):
        self.__wrapper.execute()
        if not self.__processing_events:
            self.__process_events()

    def move(self, distance: float, execute: bool = False):
        self.__wrapper.move(distance)

        if execute:
            self.execute()
            while self.status["action_status"]["move"] != 0:
                self.execute()

    def turn(self, radians: float, execute: bool = False):
        self.__wrapper.turn(radians)

        if execute:
            self.execute()
            while self.status["action_status"]["turn"] != 0:
                self.execute()

    def turn_gun(self, radians: float, execute: bool = False):
        self.__wrapper.turn_gun(radians)

        if execute:
            self.execute()
            while self.status["action_status"]["turn_gun"] != 0:
                self.execute()

    def turn_radar(self, radians: float, execute: bool = False):
        self.__wrapper.turn_radar(radians)

        if execute:
            self.execute()
            while self.status["action_status"]["turn_radar"] != 0:
                self.execute()

    def fire(self, power: float, execute: bool = False):
        self.__wrapper.fire(power)

        if execute:
            self.execute()

    def scan(self, execute: bool = False):
        self.__wrapper.scan()

        if execute:
            self.execute()

    def set_max_velocity(self, velocity: float, execute: bool = False):
        self.__wrapper.set_max_velocity(velocity)

        if execute:
            self.execute()

    def set_max_turn_rate(self, turn_rate: float, execute: bool = False):
        self.__wrapper.set_max_turn_rate(turn_rate)

        if execute:
            self.execute()

    def lock_gun_body(self, locked: bool, execute: bool = False):
        self.__wrapper.lock_gun_body(locked)

        if execute:
            self.execute()

    def lock_radar_gun(self, locked: bool, execute: bool = False):
        self.__wrapper.lock_radar_gun(locked)

        if execute:
            self.execute()

    def lock_radar_body(self, locked: bool, execute: bool = False):
        self.__wrapper.lock_radar_body(locked)

        if execute:
            self.execute()

    def wait(self, condition: Callable[[], bool]):
        self.__wrapper.wait(condition)

        self.execute()
        while not condition():
            self.execute()

    def add_custom_event(self, name: str, condition: Callable[[], bool], execute: bool = False):
        self.__wrapper.add_custom_event(name, condition)

        if execute:
            self.execute()

    def remove_custom_event(self, name: str, execute: bool = False):
        self.__wrapper.remove_custom_event(name)

        if execute:
            self.execute()

    def __process_events(self, refresh_queue: bool = False):
        assert not self.__processing_events

        if refresh_queue:
            self.__wrapper.event_manager.process()

        self.__processing_events = True
        while not self.__wrapper.event_manager.empty:
            event = self.__wrapper.event_manager.consume()

            if isinstance(event, events.BulletHitEvent):
                self.handle_bullet_hit(event)
            elif isinstance(event, events.BulletHitBulletEvent):
                self.handle_bullet_hit_bullet(event)
            elif isinstance(event, events.BulletMissedEvent):
                self.handle_bullet_missed(event)
            elif isinstance(event, events.DeathEvent):
                self.handle_death(event)
            elif isinstance(event, events.CustomEvent):
                self.handle_custom(event)
            elif isinstance(event, events.HitByBulletEvent):
                self.handle_hit_by_bullet(event)
            elif isinstance(event, events.HitRobotEvent):
                self.handle_hit_robot(event)
            elif isinstance(event, events.HitWallEvent):
                self.handle_hit_wall(event)
            elif isinstance(event, events.RobotDeathEvent):
                self.handle_robot_death(event)
            elif isinstance(event, events.ScannedRobotEvent):
                self.handle_scanned_robot(event)
            elif isinstance(event, events.SkippedTurnEvent):
                self.handle_skipped_turn(event)
            elif isinstance(event, events.StatusEvent):
                self.handle_status(event)
            elif isinstance(event, events.VictoryEvent):
                self.handle_victory(event)
            else:
                raise Exception("unknown event instance")
        self.__processing_events = False

    def handle_bullet_hit(self, event: events.BulletHitEvent):
        pass

    def handle_bullet_hit_bullet(self, event: events.BulletHitBulletEvent):
        pass

    def handle_bullet_missed(self, event: events.BulletMissedEvent):
        pass

    def handle_death(self, event: events.DeathEvent):
        pass

    def handle_custom(self, event: events.CustomEvent):
        pass

    def handle_hit_by_bullet(self, event: events.HitByBulletEvent):
        pass

    def handle_hit_robot(self, event: events.HitRobotEvent):
        pass

    def handle_hit_wall(self, event: events.HitWallEvent):
        pass

    def handle_robot_death(self, event: events.RobotDeathEvent):
        pass

    def handle_scanned_robot(self, event: events.ScannedRobotEvent):
        pass

    def handle_skipped_turn(self, event: events.SkippedTurnEvent):
        pass

    def handle_status(self, event: events.StatusEvent):
        pass

    def handle_victory(self, event: events.VictoryEvent):
        pass
