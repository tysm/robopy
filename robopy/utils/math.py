from typing import Union


def sign(x: Union[int, float]) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0
