from typing import Union

from robopy.core.objects import BattlefieldCore, BulletCore


class Battlefield:
    def __init__(self, core: BattlefieldCore):
        self.__core = core

    @property
    def width(self) -> int:
        return self.__core.width

    @property
    def height(self) -> int:
        return self.__core.height


class Bullet:
    def __init__(self, core: BulletCore):
        self.__core: BulletCore = core

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
    def power(self) -> float:
        return self.__core.power

    @property
    def owner(self) -> str:
        return self.__core.owner.name

    @property
    def victim(self) -> Union[str, None]:
        if self.__core.victim is not None:
            return self.__core.victim.name
        return None
