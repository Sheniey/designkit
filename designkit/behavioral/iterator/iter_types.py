
from abc import ABC, abstractmethod
from typing import Any, Self

from .exceptions import InvalidIteratorStateError

class IteratorBase(ABC):
    @abstractmethod
    def __iter__(self): ...

    @abstractmethod
    def __next__(self): ...


    def __getitem__(self, index: int) -> Any:
        raise InvalidIteratorStateError( operation='__getitem__()', required='next()' )
    def __setitem__(self, index: int, value: Any) -> None:
        raise InvalidIteratorStateError( operation='__setitem__()', required='append()' )
    def __delitem__(self, index: int) -> None:
        raise InvalidIteratorStateError( operation='__delitem__()', required='rollback()' )


    def __len__(self) -> int:
        return self.size


    @abstractmethod
    def is_empty(self) -> bool: ...

    @abstractmethod
    def has_next(self) -> bool: ...
    

    @abstractmethod
    def append(self, item: Any) -> None: ...

    @abstractmethod
    def copy(self) -> Self: ...


    @abstractmethod
    def peek(self) -> Any: ...

    @abstractmethod
    def next(self) -> Any: ...


    @abstractmethod
    @property
    def size(self) -> int: ...
