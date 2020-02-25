import math


def normalize(x: float, min_x: float, max_x: float, low: float = 0.0, high: float = 1.0) -> float:
    assert min_x <= x <= max_x
    assert low <= high
    return low + ((x - min_x)/(max_x - min_x))*(high - low)


def normalize_angle(x: float, degrees: bool = False, relative: bool = False) -> float:
    if degrees:
        x = math.radians(x)
    x %= math.radians(360)
    if relative:
        if x >= math.radians(180):
            x -= math.radians(360)
    return math.degrees(x) if degrees else x
