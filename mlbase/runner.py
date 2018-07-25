"""
>>> from event import event_manager as em
>>> from runner import StepManager
>>> @em.on("A")
... def _():
...   print("__A__")

>>> @em.on("B")
... def _():
...   print("__B__")

>>> step_manager = StepManager(1, 3)

>>> @step_manager
... def train_task():
...   em.emit("A")
...   @step_manager.interval(2)
...   def _():
...     em.emit("B")
__A__
__A__
__B__
__A__
"""

from typing import Callable


class StepManager():
    def __init__(self, initial_step=1, final_step=None):
        self.__initial_step = initial_step
        self.__final_step = final_step
        self.__current_step = initial_step
        self.__finished = False
        self.__check_finished()

    def __call__(self, func: Callable[[], None]):
        while not self.__finished:
            func()
            self.__current_step += 1
            self.__check_finished()

    def interval(self, n):
        def _exec(func):
            if self.__current_step % n == 0:
                func()

        return _exec

    def __check_finished(self):
        self.__finished = (self.__current_step > self.__final_step)
