
from abc import ABC, abstractmethod
from typing import Any


class Strategy[T](ABC):
    def __call__(self, data: T) -> None:
        self.execute(data)

    @abstractmethod
    def execute(self, data: T) -> None:
        pass

class Context:
    def __init__(self, strategy: Strategy[Any]) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: Strategy[Any]) -> None:
        self._strategy = strategy

    def execute_strategy(self, data: Any) -> None:
        self._strategy.execute(data)


# Example usage
import json

class JSONStrategy(Strategy[dict]):
    def execute(self, data: dict) -> None:
        print(json.dumps(data, indent=4))

class PrintStrategy(Strategy[str]):
    def execute(self, data: str) -> None:
        print(data)

class Console(Context):
    def __init__(self, strategy: Strategy[Any]) -> None:
        super().__init__(strategy)

    def display(self, data: Any) -> None:
        self.execute_strategy(data)
