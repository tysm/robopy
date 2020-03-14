import copy
from typing import Callable

import robopy.core.rules as rules
from robopy.api.objects import Battlefield
from robopy.core.execution import Statistics, Command
from robopy.core.objects import RobotCore
from robopy.wrapper.events import EventManager
from robopy.wrapper.execution import Statistics


class RobotWrapper:
    def __init__(self, core: RobotCore):
        self.__core: RobotCore = core

        self.__command: Command = Command()

        self.battlefield: Battlefield = Battlefield(core.battlefield)
        self.statistics: Statistics = Statistics(core.statistics)

        self.event_manager: EventManager = EventManager(self.statistics, core.events)

    @property
    def name(self) -> str:
        return self.__core.name

    @property
    def x(self) -> float:
        return self.__core.x

    @property
    def y(self) -> float:
        return self.__core.y

    @property
    def heading(self) -> float:
        return self.__core.heading

    @property
    def gun_heading(self) -> float:
        return self.__core.gun_heading

    @property
    def radar_heading(self) -> float:
        return self.__core.radar_heading

    @property
    def energy(self) -> float:
        return self.__core.energy

    @property
    def gun_heat(self) -> float:
        return self.__core.gun_heat

    @property
    def velocity(self) -> float:
        return self.__core.velocity

    @property
    def disabled(self) -> bool:
        return self.__core.disabled

    @property
    def status(self) -> dict:
        return self.__core.status

    def execute(self):
        #: Call the core execution.
        self.__core.execute(self.__command)

        self.__command = copy.deepcopy(self.__core.command)

        #: Process new events.
        self.event_manager.process()

    def move(self, distance: float):
        if distance == float("nan"):
            distance = 0.0

        if not self.__core.disabled:
            self.__command.move = distance

    def turn(self, radians: float):
        if radians == float("nan"):
            radians = 0.0

        if not self.__core.disabled:
            self.__command.turn = radians

    def turn_gun(self, radians: float):
        if radians == float("nan"):
            radians = 0.0

        self.__command.turn_gun = radians

    def turn_radar(self, radians: float):
        if radians == float("nan"):
            radians = 0.0

        self.__command.turn_radar = radians

    def fire(self, power: float):
        if power == float("nan"):
            power = 0.0

        self.__command.fire = power

    def scan(self):
        self.__command.scan = True

    def set_max_velocity(self, velocity: float):
        self.__command.max_velocity = min(abs(velocity), rules.MAX_VELOCITY)

    def set_max_turn_rate(self, turn_rate: float):
        self.__command.max_turn_rate = min(abs(turn_rate), rules.MAX_TURN_RATE)

    def lock_gun_body(self, locked: bool):
        self.__command.lock_gun_body = locked

    def lock_radar_gun(self, locked: bool):
        self.__command.lock_radar_gun = locked

    def lock_radar_body(self, locked: bool):
        self.__command.lock_radar_body = locked

    def wait(self, condition: Callable[[], bool]):
        self.__command.wait = condition

    def add_custom_event(self, name: str, condition: Callable[[], bool]):
        self.__core.custom_events[name] = condition

    def remove_custom_event(self, name: str):
        self.__core.custom_events.pop(name)
