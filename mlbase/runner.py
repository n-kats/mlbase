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
        self._initial_step = initial_step
        self._final_step = final_step
        self._current_step = initial_step
        self._finished = False
        self._check_finished()

    def __call__(self, func: Callable[[], None]):
        while not self._finished:
            func()
            self._current_step += 1
            self._check_finished()

    def interval(self, n):
        def _exec(func):
            if self._current_step % n == 0:
                func()

        return _exec

    def _check_finished(self):
        self._finished = (self._current_step > self._final_step)
