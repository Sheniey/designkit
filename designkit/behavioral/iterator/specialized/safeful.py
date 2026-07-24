
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Iterable

from ..core import Iterator
from ..exceptions import (
    NoMoreItemsError,
    NotStartedYetError
)
from ..iter_types import IteratorBase

class ConfirmAction(Enum):
    CONFIRMED = auto()
    CANCELED = auto()
    UNCONFIRMED = auto()


@dataclass
class _Confirmer[I]:
    fx: Callable[..., I] = field(repr=False)
    _action: ConfirmAction = ConfirmAction.UNCONFIRMED

    def confirm(self, *args: Any, **kwargs: Any) -> I:
        self._action = ConfirmAction.CONFIRMED
        return self.fx(*args, **kwargs)
        
    def cancel(self) -> None:
        self._action = ConfirmAction.CANCELED
        return # unnecessary but for clarity

    def preview(self) -> ConfirmAction:
        return self._action


class SafeIterator[I](IteratorBase):
    def __init__(self, collection: Iterable[I]) -> None:
        self.__collection: Iterable[I] = collection
        self.__iterator: Iterator[Iterable[I]] = Iterator(collection)
    


    def __str__(self) -> str:
        return f"{self.__class__.__name__}( {len(self)} total items, {self.__iterator.size()} remaining )"
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"    length={len(self.__collection)}, "
            f"    index={self.__iterator.index}, "
            f"    remaining={self.__iterator.remaining}"
            f")"
        )



    def __iter__(self) -> SafeIterator[I]:
        return self

    def __next__(self) -> _Confirmer[I]:
        if self.__iterator.index >= len(self.__collection):
            raise NoMoreItemsError(self) from StopIteration
        return self.next()
    


    def __len__(self) -> int:
        return self.size()
    
    def size(self) -> int:
        return len(self.__collection)
    
    
    
    def is_empty(self) -> bool:
        return self.__iterator.is_empty()
    
    def has_next(self) -> bool:
        return self.__iterator.has_next()



    def append(self, item: I) -> None:
        self.__iterator.append(item)

    def copy(self) -> SafeIterator[I]:
        return SafeIterator(self.__collection)



    def peek(self) -> _Confirmer[I]:
        # precatch the exception before to confirm the action
        # so, this code is double-executed
        if self.__iterator.index >= len(self.__collection):
            raise NoMoreItemsError(self)
        return _Confirmer(self.__iterator.peek)

    def next(self) -> _Confirmer[I]:
        return _Confirmer(self.__iterator.next)
    
    def rollback(self) -> None:
        self.__iterator.rollback()


    
    @property
    def current(self) -> _Confirmer[I]:
        # precatch the exception before to confirm the action
        # so, this code is double-executed
        if self.__iterator.index == 0:
            raise NotStartedYetError(self)
        return _Confirmer(self.__iterator.current)

    @property
    def index(self) -> int:
        return self.__iterator.index
    
    @property
    def remaining(self) -> int:
        return self.__iterator.remaining
