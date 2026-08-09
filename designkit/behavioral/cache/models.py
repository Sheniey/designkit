
from abc import ABC, abstractmethod

_MISSING = object()

class AbstractCache[T](ABC):
    @abstractmethod
    def get(self, key: str) -> T:
        ...

    @abstractmethod
    def put(self, key: str, value: T) -> None:
        ...
