
from abc import ABC, abstractmethod
from enum import Enum

class Mediator[S, E: Enum](ABC):
    def __call__(self, sender: S, event: E) -> None:
        self.notify(sender, event)

    @abstractmethod
    def notify(self, sender: S, event: E) -> None:
        pass

class Colleague(ABC):
    def __init__(self, mediator: Mediator) -> None:
        self.mediator: Mediator = mediator
