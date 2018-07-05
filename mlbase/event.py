"""
>>> from event import event_manager
>>> @event_manager.on("A")
... def _():
...   print('Hello')
>>> @event_manager.on("B")
... def _():
...   print('World')

>>> event_manager.emit("A")
Hello
>>> event_manager.emit("B")
World
"""


class EventManager:
    def __init__(self):
        self._event_dict = {}
        self._finished = False

    def emit(self, key, *args, **kwargs):
        return self._event_dict[key](*args, **kwargs)

    def on(self, key):
        def _exec(func):
            self._event_dict[key] = func

        return _exec


event_manager = EventManager()
