import math

import robopy.api.events as events
from robopy.api.robot import Robot


class Target(Robot):
    def __init__(self, wrapper):
        super().__init__(wrapper)

        #: Initially, we'll move when life hits 80.
        self.trigger: int = 80

    def _run(self):
        #: Add a custom event named "trigger hit".
        def condition() -> bool:
            return self.energy <= self.trigger
        self.add_custom_event("trigger hit", condition, execute=True)
        while True:
            self.execute()  #: Custom events are checked strictly during execution.

    def handle_custom(self, e: events.CustomEvent):
        if e.name == "trigger hit":
            #: Our custom event "trigger hit" went off.
            #: Adjust the trigger value, or else the event will fire again and again and again...
            self.trigger -= 20
            print("Ouch, down to " + str(self.energy + 0.5) + " energy.")  #: TODO support robot print separately.
            #: Move around a bit.
            self.turn(-math.radians(65), execute=True)
            self.move(100, execute=True)
