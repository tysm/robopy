import math


ACCELERATION: float = 1

DECELERATION: float = 2

MAX_VELOCITY: float = 8

MIN_BULLET_POWER: float = 0.1

MAX_BULLET_POWER: float = 3.0

MAX_TURN_RATE: float = math.radians(10)

GUN_TURN_RATE: float = math.radians(20)

GUN_COOLING_RATE: float = 0.1

RADAR_TURN_RATE: float = math.radians(45)

RADAR_RANGE: int = 1200

ROBOT_HIT_DAMAGE: float = 0.6


def get_max_deceleration(velocity: float) -> float:
    deceleration_time = velocity / DECELERATION
    acceleration_time = 1 - deceleration_time
    return min(1.0, deceleration_time) * DECELERATION + max(0.0, acceleration_time) * ACCELERATION


def get_max_velocity(distance: float) -> float:
    deceleration_time = max(1, math.ceil((math.sqrt((4 * 2 / DECELERATION) * distance + 1) - 1) / 2))
    if deceleration_time == float("inf"):
        return MAX_VELOCITY
    deceleration_distance = (deceleration_time / 2) * (deceleration_time - 1) * DECELERATION
    return ((deceleration_time - 1) * DECELERATION) + ((distance - deceleration_distance) / deceleration_time)


def get_velocity(velocity: float, distance: float, max_velocity: float = MAX_VELOCITY) -> float:
    assert abs(max_velocity) <= MAX_VELOCITY

    if distance < 0:
        # If the distance is negative, then change it to be positive
        # and change the sign of the input velocity and the result
        return -get_velocity(-velocity, -distance, max_velocity)

    if distance == float("inf"):
        goal_velocity = max_velocity
    else:
        goal_velocity = min(max_velocity, get_max_velocity(distance))

    if velocity >= 0:
        return max(velocity - DECELERATION, min(goal_velocity, velocity + ACCELERATION))
    return max(velocity - ACCELERATION, min(goal_velocity, velocity + get_max_deceleration(-velocity)))


def get_distance_until_stop(velocity: float, max_velocity: float = MAX_VELOCITY) -> float:
    assert abs(max_velocity) <= MAX_VELOCITY

    distance, velocity = 0, abs(velocity)
    while velocity > 0:
        velocity = get_velocity(velocity, 0, max_velocity)
        distance += velocity
    return distance


def get_turn_rate(velocity: float, max_turn_rate: float = MAX_TURN_RATE) -> float:
    assert -MAX_VELOCITY <= velocity <= MAX_VELOCITY
    assert max_turn_rate <= MAX_TURN_RATE
    return max_turn_rate - math.radians(0.75 * abs(velocity))


def get_wall_hit_damage(velocity: float) -> float:
    assert -MAX_VELOCITY <= velocity <= MAX_VELOCITY
    return max(0.0, abs(velocity) * 0.5 - 1)


def get_gun_heat(power: float) -> float:
    assert MIN_BULLET_POWER <= power <= MAX_BULLET_POWER
    return 1 + power / 5


def get_bullet_damage(power: float) -> float:
    assert MIN_BULLET_POWER <= power <= MAX_BULLET_POWER
    return 4 * power + 2 * max(0.0, (power - 1))


def get_bullet_hit_bonus(power: float) -> float:
    assert MIN_BULLET_POWER <= power <= MAX_BULLET_POWER
    return 3 * power


def get_bullet_velocity(power: float) -> float:
    assert MIN_BULLET_POWER <= power <= MAX_BULLET_POWER
    return 20 - 3 * power
