import random
import time
from threading import Thread, Semaphore
from typing import Dict, List, Tuple, Type

from robopy.api.robot import Robot
from robopy.core.events import EventKind
from robopy.core.execution import Statistics, BattleState
from robopy.core.objects import BattlefieldCore, BulletCore, RobotCore
from robopy.wrapper.robot import RobotWrapper


class Battle(Thread):
    def __init__(self, battlefield_dimensions: Tuple[int, int], robot_classes: List[Type[Robot]]):
        super().__init__(name="BattleThread")

        self.robot_classes: List[Type[Robot]] = robot_classes

        self.statistics: Statistics = Statistics(len(robot_classes))
        self.battlefield: BattlefieldCore = BattlefieldCore(battlefield_dimensions)

        self.robots: List[RobotCore] = []
        self.robot_threads: Dict[RobotCore, Robot] = {}
        self.bullets: List[BulletCore] = []

        self.semaphore: Semaphore = Semaphore()

    @property
    def shuffled_robot_classes(self) -> Tuple[Type[Robot]]:
        robot_classes = list(self.robot_classes)
        random.shuffle(robot_classes)
        return tuple(robot_classes)

    @property
    def shuffled_robots(self) -> Tuple[RobotCore]:
        robots = list(self.robots)
        random.shuffle(robots)
        return tuple(robots)

    @property
    def shuffled_bullets(self) -> Tuple[BulletCore]:
        bullets = list(self.bullets)
        random.shuffle(bullets)
        return tuple(bullets)

    def run(self):
        assert self.statistics.battle_state is None

        self.statistics.battle_state = BattleState.RUNNING

        self._setup()
        self._main()

        self.stop()

    def stop(self):
        assert self.statistics.battle_state in (BattleState.RUNNING, BattleState.ENDED)

        self.statistics.battle_state = BattleState.STOPPED

        #: TODO wait for robot threads to stop.
        #: TODO force non-stopped threads to stop.
        #: TODO apply penalties for those robots which prevented its thread from stopping.

    def _setup(self):
        robot_names = {}
        for robot_class in self.shuffled_robot_classes:
            name = robot_class.__name__
            if name not in robot_names:
                robot_names[name] = 1
            else:
                robot_names[name] += 1
                name = f"{name}({robot_names[name] - 1})"

            robot = RobotCore(name, self.statistics, self.battlefield, self.shuffled_robots)
            self.robots.append(robot)

            thread = robot_class(RobotWrapper(robot))
            self.robot_threads[robot] = thread

    def _main(self):
        #: Publish Status event of the first turn.
        for robot in self.shuffled_robots:
            robot.add_event(EventKind.Status, (robot.status,))

        #: Start the control processing.
        for robot in self.shuffled_robots:
            self.robot_threads[robot].start()

        while self.statistics.battle_state is BattleState.RUNNING:
            time.sleep(0.1)  #: TODO what's the best amount of time per turn.

            #: Usually there's a control step on the main loop of games.
            #: However the control step of this game is written by the competitors,
            #: inside the robots' run method.

            #: Process alive robots that have locked robots only.
            robots = tuple(r for r in self.shuffled_robots if not r.dead and r.locked)

            #: Logic step.
            self._logic(robots)

            #: Wake up the processed robots.
            for robot in robots:
                #: Even dead robots are released to process its death.
                robot.release()

    def _logic(self, robots: Tuple[RobotCore]):
        #: Make sure that the battle rendering doesn't catch
        #: any semi-updated information from robots or battle statistics.
        self.semaphore.acquire()

        for robot in robots:
            #: Robots can die during this loop,
            #: thus they can't execute any action.
            if robot.dead:
                continue

            #: Try to fire a bullet.
            bullet = robot.fire()
            if bullet is not None:
                self.bullets.append(bullet)

            #: Update the robot.
            robot.update(self.shuffled_robots)

        #: Update bullets.
        bullets = []
        for bullet in self.shuffled_bullets:
            bullet.update(self.shuffled_robots, self.shuffled_bullets)
            if not bullet.inactive:
                bullets.append(bullet)
        self.bullets = bullets

        #: Compute alive robots.
        self.statistics.alive_robots = sum(int(not robot.dead) for robot in self.shuffled_robots)

        if self.statistics.alive_robots <= 1:
            #: There's a battle winner, thus the battle is ended.
            self.statistics.battle_state = BattleState.ENDED

            if self.statistics.alive_robots == 1:
                winner = None
                for robot in self.shuffled_robots:
                    if robot.dead:
                        continue
                    winner = robot
                assert winner is not None

                #: Publish Victory event.
                winner.add_event(EventKind.Victory, ())
        else:
            self.statistics.tick()

            #: The following event publishing or actions
            #: are performed right after the tick because
            #: they publish information of the initial
            #: game state of the following turn
            #: (e.g. robot position).

            #: Perform scan.
            for robot in robots:
                #: Robots could've died during past updates,
                #: thus they can't perform scan.
                if robot.dead:
                    continue
                robot.scan(self.shuffled_robots)

            #: Publish Custom events.
            for robot in robots:
                #: Robots could've died during past updates,
                #: thus they won't receive its custom events.
                if robot.dead:
                    continue
                for name, condition in robot.custom_events.items():
                    if condition():
                        robot.add_event(EventKind.Custom, (name,))

            #: Publish Skipped Turn event.
            for robot in self.shuffled_robots:
                if robot.dead or robot in robots:
                    continue
                robot.add_event(EventKind.SkippedTurn, (self.statistics.time - 1,))

            #: Publish Status event with updated information.
            for robot in self.shuffled_robots:
                #: Dead robots won't receive this event anymore.
                if robot.dead:
                    continue
                robot.add_event(EventKind.Status, (robot.status,))

        self.semaphore.release()
