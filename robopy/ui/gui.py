from threading import Thread

import cv2

from robopy.core.battle import Battle
from robopy.core.execution import BattleState


class GUI(Thread):
    def __init__(self, battle: Battle, fps: int = 60):
        super().__init__(name="GUIThread")

        self.battle: Battle = battle
        self.fps: int = fps

    def run(self):
        self.render()
        while self.battle.statistics.battle_state is BattleState.RUNNING:
            self.render(1000 // self.fps)

    def render(self, wait: int = 1):
        self.battle.semaphore.acquire()
        screen = self.battle.battlefield.paint()
        for bullet in self.battle.bullets:
            screen = bullet.paint(screen)
        for robot in self.battle.shuffled_robots:
            if robot.dead:
                continue
            screen = robot.paint(screen)
        self.battle.semaphore.release()
        cv2.imshow("battlefield", cv2.flip(screen, 0))
        cv2.waitKey(wait)
