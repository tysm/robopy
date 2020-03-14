import math
import random
from threading import Lock
from typing import Callable, Dict, Tuple, Union

import cv2
import numpy as np
import shapely.geometry as geometry

import robopy.core.rules as rules
from robopy.core.events import EventCore, EventKind
from robopy.core.execution import Statistics, Command, BattleState, BulletState, RobotState, InterruptedExecutionException
from robopy.utils import normalization
from robopy.utils.math import sign
from robopy.utils.threading import List as ThreadingList


class BattlefieldCore:
    def __init__(self, dimensions: Tuple[int, int]):
        self.width = dimensions[0]
        self.height = dimensions[1]

    def paint(self) -> np.ndarray:
        screen = np.zeros((self.height, self.width, 3), np.uint8)
        return screen


class BulletCore:
    RADIUS: int = 3

    def __init__(self, battlefield: BattlefieldCore, x: float, y: float, heading: float, owner: 'RobotCore', power: float):
        self.battlefield: BattlefieldCore = battlefield
        self.owner: RobotCore = owner
        self.power: float = power

        self.x: float = x
        self.y: float = y

        self.heading: float = heading

        self.state = BulletState.FIRED  #: TODO how to typify enum?
        self.victim: Union[RobotCore, None] = None
        self.line: geometry.LineString = geometry.LineString([(x, y), (x, y)])

    @property
    def damage(self) -> float:
        return rules.get_bullet_damage(self.power)

    @property
    def hit_bonus(self) -> float:
        return rules.get_bullet_hit_bonus(self.power)

    @property
    def velocity(self) -> float:
        return rules.get_bullet_velocity(self.power)

    @property
    def active(self) -> bool:
        return self.state in (BulletState.FIRED, BulletState.MOVING)

    @property
    def exploded(self) -> bool:
        return self.state in (BulletState.HIT_VICTIM, BulletState.HIT_BULLET, BulletState.HIT_WALL)

    @property
    def inactive(self) -> bool:
        return self.state is BulletState.INACTIVE

    def update(self, robots: Tuple['RobotCore'], bullets: Tuple['BulletCore']):
        if self.active:
            #: Update coordinates.
            self.update_coordinates()

            #: Check for wall collisions.
            self.check_wall_collision()

            #: Check for robot collisions.
            if self.active:
                self.check_robot_collision(robots)

            #: Check for bullet collisions.
            if self.active:
                self.check_bullet_collision(bullets)
        elif self.exploded:
            self.state = BulletState.INACTIVE

    def update_coordinates(self):
        last_x, last_y = self.x, self.y

        self.x += self.velocity * math.sin(self.heading)
        self.y += self.velocity * math.cos(self.heading)

        self.line = geometry.LineString([(last_x, last_y), (self.x, self.y)])
        self.state = BulletState.MOVING

    def check_wall_collision(self):
        min_x, min_y = 0 + BulletCore.RADIUS, 0 + BulletCore.RADIUS
        max_x, max_y = self.battlefield.width - BulletCore.RADIUS, self.battlefield.height - BulletCore.RADIUS

        if not min_x <= self.x <= max_x or not min_y <= self.y <= max_y:
            self.state = BulletState.HIT_WALL

            #: Add BulletMissed event to the owner's process queue.
            self.owner.add_event(EventKind.BulletMissed, (self,))

    def check_robot_collision(self, robots: Tuple['RobotCore']):
        for robot in robots:
            if robot is self.owner or robot.dead:
                continue
            elif self.line.intersects(robot.polygon):
                robot.update_energy(-self.damage, True, robots)

                self.owner.update_energy(self.hit_bonus)

                self.victim = robot
                self.state = BulletState.HIT_VICTIM

                #: Add BulletHit event to the owner's process queue.
                self.owner.add_event(EventKind.BulletHit, (robot.name, robot.energy, self))

                #: Add HitByBullet event to the robot's process queue.
                robot.add_event(
                    EventKind.HitByBullet,
                    (
                        normalization.normalize_angle(self.heading + math.radians(180) - robot.heading, relative=True),
                        self
                    )
                )
                break

    def check_bullet_collision(self, bullets: Tuple['BulletCore']):
        for bullet in bullets:
            if bullet is self or bullet.owner is self.owner or not bullet.active:
                continue
            elif self.line.intersects(bullet.line):
                point = self.line.intersection(bullet.line)

                self.x = point.x
                self.y = point.y
                self.state = BulletState.HIT_BULLET

                bullet.x = point.x
                bullet.y = point.y
                bullet.state = BulletState.HIT_BULLET

                #: Add BulletHitBullet event to the owner's process queue.
                self.owner.add_event(EventKind.BulletHitBullet, (self, bullet))

                #: Add BulletHitBullet event to the robot's process queue.
                bullet.owner.add_event(EventKind.BulletHitBullet, (bullet, self))
                break

    def paint(self, screen: np.ndarray) -> np.ndarray:
        center = (int(self.x), int(self.y))
        screen = cv2.circle(screen, center, 0, (255, 0, 0), 2*math.ceil(self.power))
        return screen


class RobotCore:
    WIDTH: int = 36
    HEIGHT: int = 36

    HALF_WIDTH: int = WIDTH // 2
    HALF_HEIGHT: int = HEIGHT // 2

    def __init__(self, name: str, statistics: Statistics, battlefield: BattlefieldCore, robots: Tuple['RobotCore']):
        self.name: str = name
        self.statistics: statistics = statistics
        self.battlefield: BattlefieldCore = battlefield

        self.x: float = normalization.normalize(
            random.random(), 0, 1,
            0 + RobotCore.HALF_WIDTH, battlefield.width - RobotCore.HALF_WIDTH
        )
        self.y: float = normalization.normalize(
            random.random(), 0, 1,
            0 + RobotCore.HALF_HEIGHT, battlefield.height - RobotCore.HALF_HEIGHT
        )

        heading = random.random() * math.radians(360)
        self.heading: float = heading
        self.gun_heading: float = heading
        self.radar_heading: float = heading

        self.energy: float = 100
        self.gun_heat: float = 3
        self.velocity: float = 0

        self.in_collision: bool = False
        self.over_driving: bool = False

        self.lock: Lock = Lock()
        self.state = RobotState.ACTIVE  #: TODO how to typify enum?
        self.command: Command = Command()
        self.events: ThreadingList[EventCore] = ThreadingList()
        self.custom_events: Dict[str, Callable[[], bool]] = {}

        self.polygon: geometry.Polygon = geometry.box(
            int(self.x - RobotCore.HALF_WIDTH),
            int(self.y - RobotCore.HALF_HEIGHT),
            int(self.x + RobotCore.HALF_WIDTH),
            int(self.y + RobotCore.HALF_HEIGHT)
        )

        center = (int(self.x), int(self.y))
        sin = math.sin(self.radar_heading)
        cos = math.cos(self.radar_heading)
        end = (int(center[0] + rules.RADAR_RANGE * sin), int(center[1] + rules.RADAR_RANGE * cos))
        self.scan_arc: geometry.Polygon = geometry.Polygon([center, end, end])

        def valid_coordinates() -> bool:
            for robot in robots:
                if self.polygon.intersects(robot.polygon):
                    return False
            return True

        while not valid_coordinates():
            self.x: float = normalization.normalize(
                random.random(), 0, 1,
                0 + RobotCore.HALF_WIDTH, battlefield.width - RobotCore.HALF_WIDTH
            )
            self.y: float = normalization.normalize(
                random.random(), 0, 1,
                0 + RobotCore.HALF_HEIGHT, battlefield.height - RobotCore.HALF_HEIGHT
            )
            self.update_polygon()
            self.update_scan_arc(self.radar_heading)

    @property
    def disabled(self) -> bool:
        return self.energy == 0 and not self.dead

    @property
    def dead(self) -> bool:
        return self.state is RobotState.DEAD

    @property
    def status(self) -> dict:
        _status = dict(
            time=self.statistics.time,
            name=self.name,
            x=self.x,
            y=self.y,
            heading=self.heading,
            gun_heading=self.gun_heading,
            radar_heading=self.radar_heading,
            energy=self.energy,
            gun_heat=self.gun_heat,
            velocity=self.velocity,
            disabled=self.disabled,
            dead=self.dead,
            action_status=self.command.status
        )
        return _status

    @property
    def locked(self) -> bool:
        return self.lock.locked()

    def release(self):
        self.lock.release()

    def execute(self, command: Command):
        #: Robots can't execute if they are dead or the battle is not running.
        if self.dead:
            raise InterruptedExecutionException("robot is dead")
        elif self.statistics.battle_state is not BattleState.RUNNING:
            raise InterruptedExecutionException("battle is not running")

        self.command = command

        #: Wait until the battle thread finish the updates.
        self.lock.acquire()

    def fire(self) -> Union[BulletCore, None]:
        assert not self.dead

        power = min(rules.MAX_BULLET_POWER, self.energy, self.command.fire)
        if power >= rules.MIN_BULLET_POWER and self.gun_heat == 0:
            self.update_energy(-power)
            self.gun_heat = rules.get_gun_heat(power)
            bullet = BulletCore(self.battlefield, self.x, self.y, self.gun_heading, self, power)
        else:
            bullet = None
        self.command.fire = 0.0
        return bullet

    def scan(self, robots: Tuple['RobotCore']):
        assert not self.dead

        if self.command.scan:
            for robot in robots:
                if robot is self or robot.dead:
                    continue
                if self.scan_arc.intersects(robot.polygon):
                    angle = math.atan2(robot.x - self.x, robot.y - self.y)
                    bearing = normalization.normalize_angle(angle - self.heading, relative=True)
                    distance = math.sqrt((robot.x - self.x)**2 + (robot.y - self.y)**2)

                    #: Add ScannedRobot event to the process queue.
                    self.add_event(
                        EventKind.ScannedRobot,
                        (
                            robot.name,
                            robot.heading,
                            robot.energy,
                            robot.velocity,
                            bearing,
                            distance
                        )
                    )
        self.command.scan = False

    def update(self, robots: Tuple['RobotCore']):
        assert not self.dead

        self.state = RobotState.ACTIVE

        last_heading = self.heading
        last_gun_heading = self.gun_heading
        last_radar_heading = self.radar_heading
        last_x, last_y = self.x, self.y

        #: Update the gun heat.
        self.update_gun_heat()

        #: Update the heading.
        if not self.disabled and not self.in_collision:
            self.update_heading()

        #: Update the gun heading.
        self.update_gun_heading()

        #: Update the radar heading.
        self.update_radar_heading()

        if not self.disabled:
            #: Update the velocity.
            self.update_velocity()

            #: Update the coordinates.
            self.update_coordinates()

            #: Check for wall collisions.
            self.check_wall_collision()

            #: Check for robot collisions.
            self.check_robot_collision(robots)

        #: Update the scan arc.
        self.update_scan_arc(last_radar_heading)

        #: If the robot has executed any moving step,
        #: then it executes a scan automatically.
        if last_heading != self.heading \
                or last_gun_heading != self.gun_heading \
                or last_radar_heading != self.radar_heading \
                or last_x != self.x \
                or last_y != self.y:
            self.command.scan = True

    def update_coordinates(self):
        if self.velocity == 0 and self.over_driving:
            self.command.move = 0
            self.over_driving = False

        if sign(self.command.move * self.velocity) != -1:
            if rules.get_distance_until_stop(self.velocity, self.command.max_velocity) > abs(self.command.move):
                self.over_driving = True
            else:
                self.over_driving = False

        if self.velocity != 0:
            self.x += self.velocity * math.sin(self.heading)
            self.y += self.velocity * math.cos(self.heading)
            self.update_polygon()
        self.command.move -= self.velocity

    def update_heading(self):
        max_turn_rate = rules.get_turn_rate(self.velocity, self.command.max_turn_rate)

        angle = min(max_turn_rate, max(-max_turn_rate, self.command.turn))
        self.heading = normalization.normalize_angle(self.heading + angle)
        if self.command.lock_gun_body:
            self.gun_heading = normalization.normalize_angle(self.gun_heading + angle)
        if self.command.lock_radar_body:
            self.radar_heading = normalization.normalize_angle(self.radar_heading + angle)
        self.command.turn -= angle

    def update_gun_heading(self):
        angle = min(rules.GUN_TURN_RATE, max(-rules.GUN_TURN_RATE, self.command.turn_gun))
        self.gun_heading = normalization.normalize_angle(self.gun_heading + angle)
        if self.command.lock_radar_gun:
            self.radar_heading = normalization.normalize_angle(self.radar_heading + angle)
        self.command.turn_gun -= angle

    def update_radar_heading(self):
        angle = min(rules.RADAR_TURN_RATE, max(-rules.RADAR_TURN_RATE, self.command.turn_radar))
        self.radar_heading = normalization.normalize_angle(self.radar_heading + angle)
        self.command.turn_radar -= angle

    def update_gun_heat(self):
        self.gun_heat = max(0.0, self.gun_heat - rules.GUN_COOLING_RATE)

    def update_velocity(self):
        self.velocity = rules.get_velocity(self.velocity, self.command.move, self.command.max_velocity)

    def update_energy(self, delta: float, kill: bool = False, robots: Union[Tuple['RobotCore'], None] = None):
        if kill:
            #: Robots are required to publish possible death.
            assert robots is not None

        self.energy = max(0, self.energy + delta)
        if self.energy == 0:
            self.command.move = 0.0
            self.command.turn = 0.0
            if kill:
                self.kill(robots)

    def update_polygon(self):
        center = (int(self.x), int(self.y))

        start = (int(center[0] - RobotCore.HALF_WIDTH), int(center[1] - RobotCore.HALF_HEIGHT))
        end = (int(center[0] + RobotCore.HALF_WIDTH), int(center[1] + RobotCore.HALF_HEIGHT))
        bounds = (*start, *end)

        self.polygon = geometry.box(*bounds)

    def update_scan_arc(self, start_angle: float):
        center = (int(self.x), int(self.y))

        sin = math.sin(start_angle)
        cos = math.cos(start_angle)
        start = (int(center[0] + rules.RADAR_RANGE * sin), int(center[1] + rules.RADAR_RANGE * cos))

        sin = math.sin(self.radar_heading)
        cos = math.cos(self.radar_heading)
        end = (int(center[0] + rules.RADAR_RANGE * sin), int(center[1] + rules.RADAR_RANGE * cos))

        self.scan_arc = geometry.Polygon([center, start, end])

    def check_wall_collision(self):
        min_x, min_y = 0 + RobotCore.HALF_WIDTH, 0 + RobotCore.HALF_HEIGHT
        max_x, max_y = self.battlefield.width - RobotCore.HALF_WIDTH, self.battlefield.height - RobotCore.HALF_HEIGHT

        hit_wall = False
        adjust_x, adjust_y, bearing = 0, 0, 0

        #: FIXME normally, "+|- 1e-10" wouldn't
        #: be necessary to check if a robot
        #: collides with a wall, but given the
        #: precision in float operations and
        #: the calculation of robot angles,
        #: some robots get unwanted collisions
        #: with walls when they try to run
        #: perpendicular to them
        #: (e.g. the sample robot Walls).
        if self.x + 1e-10 < min_x:
            hit_wall = True
            adjust_x = min_x - self.x
            bearing = normalization.normalize_angle(math.radians(270) - self.heading, relative=True)
        elif self.x - 1e-10 > max_x:
            hit_wall = True
            adjust_x = max_x - self.x
            bearing = normalization.normalize_angle(math.radians(90) - self.heading, relative=True)
        elif self.y + 1e-10 < min_y:
            hit_wall = True
            adjust_y = min_y - self.y
            bearing = normalization.normalize_angle(math.radians(180) - self.heading, relative=True)
        elif self.y - 1e-10 > max_y:
            hit_wall = True
            adjust_y = max_y - self.y
            bearing = normalization.normalize_angle(-self.heading, relative=True)

        if hit_wall:
            #: Add HitWall event to the process queue.
            self.add_event(EventKind.HitWall, (bearing,))

            #: Only adjust both x and y values if hitting wall at an angle != 90.
            if (self.heading % math.radians(90)) != 0:
                tan = math.tan(self.heading)
                #: If it hits bottom or top wall.
                if adjust_x == 0:
                    adjust_x = adjust_y * tan
                #: If it hits a side wall.
                elif adjust_y == 0:
                    adjust_y = adjust_x / tan
                #: If the robot hits 2 walls at the same time (rare, but just in case).
                elif abs(adjust_x / tan) > adjust_y:
                    adjust_y = adjust_x / tan
                elif abs(adjust_y * tan) > adjust_x:
                    adjust_x = adjust_y * tan

            self.x = min(max_x, max(min_x, self.x + adjust_x))
            self.y = min(max_y, max(min_y, self.y + adjust_y))

            self.update_energy(-rules.get_wall_hit_damage(self.velocity))

            self.velocity = 0
            self.command.move = 0.0

            self.state = RobotState.HIT_WALL
            self.update_polygon()

    def check_robot_collision(self, robots: Tuple['RobotCore']):
        self.in_collision = False
        for robot in robots:
            if robot is self or robot.dead:
                continue
            elif self.polygon.intersects(robot.polygon):
                angle = math.atan2(robot.x - self.x, robot.y - self.y)
                bearing = normalization.normalize_angle(angle - self.heading, relative=True)

                collision = (self.velocity > 0 and -math.radians(90) < bearing < math.radians(90)) \
                    or (self.velocity < 0 and (bearing < -math.radians(90) or bearing > math.radians(90)))
                if collision:
                    self.in_collision = True

                    #: TODO shouldn't be last_x and last_y?
                    #: Imagine if it hits more than one robot.
                    self.x -= self.velocity * math.sin(self.heading)
                    self.y -= self.velocity * math.cos(self.heading)
                    #: TODO shouldn't update the polygon box here?
                    #: Imagine if it hits another robot on the next loop iteration.

                    self.update_energy(-rules.ROBOT_HIT_DAMAGE, True, robots)
                    robot.update_energy(-rules.ROBOT_HIT_DAMAGE, True, robots)

                    self.velocity = 0
                    self.command.move = 0.0

                    #: Add HitRobot event to the process queue.
                    self.add_event(EventKind.HitRobot, (robot.name, robot.energy, bearing, True))

                    #: Add HitRobot event to the robot process queue.
                    robot_bearing = normalization.normalize_angle(
                        math.radians(180) + angle - robot.heading,
                        relative=True
                    )
                    robot.add_event(EventKind.HitRobot, (self.name, self.energy, robot_bearing, False))
        if self.in_collision:
            self.state = RobotState.HIT_ROBOT
            self.update_polygon()

    def kill(self, robots: Tuple['RobotCore']):
        assert not self.dead

        self.state = RobotState.DEAD

        #: Add Death event to the process queue.
        self.add_event(EventKind.Death, ())

        #: Publish the death to others robots alive.
        for robot in robots:
            if robot is self or robot.dead:
                continue
            robot.add_event(EventKind.RobotDeath, (self.name,))

    def paint(self, screen: np.ndarray) -> np.ndarray:
        center = (int(self.x), int(self.y))

        min_x, min_y, max_x, max_y = self.polygon.bounds
        start, end = (int(min_x), int(min_y)), (int(max_x), int(max_y))
        screen = cv2.rectangle(screen, start, end, (0, 0, 255), 2)

        sin = math.sin(self.heading)
        cos = math.cos(self.heading)
        front = (int(center[0] + 18 * sin), int(center[1] + 18 * cos))
        screen = cv2.line(screen, center, front, (0, 0, 255), 2)

        sin = math.sin(self.gun_heading)
        cos = math.cos(self.gun_heading)
        front = (int(center[0] + 12 * sin), int(center[1] + 12 * cos))
        screen = cv2.line(screen, center, front, (0, 255, 0), 2)

        sin = math.sin(self.radar_heading)
        cos = math.cos(self.radar_heading)
        front = (int(center[0] + 6 * sin), int(center[1] + 6 * cos))
        screen = cv2.line(screen, center, front, (255, 0, 0), 2)

        #: cv2.fillConvexPoly requires points in int32.
        points = np.asarray(list(self.scan_arc.exterior.coords)[:3], "int32")
        cv2.fillConvexPoly(screen, points, (255, 196, 191))

        return screen

    def add_event(self, kind: EventKind, args: tuple):
        self.events.append(EventCore(self.statistics.time, kind, args))
