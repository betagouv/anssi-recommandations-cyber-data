from time import sleep
from typing import Callable


class Interval:
    _pause: Callable[[int], None] = sleep

    @staticmethod
    def pause() -> None:
        return Interval._pause(2)

    @staticmethod
    def frise() -> None:
        Interval._pause = lambda _: None


class AdaptateurInterval:
    @staticmethod
    def pause() -> None:
        return Interval.pause()
