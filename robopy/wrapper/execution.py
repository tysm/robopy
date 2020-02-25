from robopy.core.execution import Statistics as StatisticsCore


class Statistics:
    def __init__(self, core: StatisticsCore):
        self.__core: StatisticsCore = core

    @property
    def time(self) -> int:
        return self.__core.time

    @property
    def robots(self) -> int:
        return self.__core.robots

    @property
    def alive_robots(self) -> int:
        return self.__core.alive_robots
