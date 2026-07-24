
from dataclasses import dataclass, field
from typing import Callable, Sequence
from functools import total_ordering
from designkit_utils.extras import IDENT
from designkit_utils.generators import uuid

from .iter_types import IteratorBase
from .exceptions import (
    UnsupportedOperationError,
    InvalidIteratorStateError,
    IndexOutOfBoundsError,
    NO_MORE_ITEMS_ERROR,
    IterationNotStartedError,
    SavepointIdMismatchError
)



@dataclass(eq=False, repr=False)
@total_ordering
class Savepoint:
    index: int = field(default=0)
    instance_id: int = field(default_factory=uuid)

    # ==================================================
    # Representation
    # ==================================================
 
    def __str__(self) -> str:
        return f'Savepoint( at {self.index} for ID {self.instance_id} )'
    
    def __repr__(self) -> str:
        return (
            f'Savepoint(\n'
            f'{IDENT}' f'index={self.index},\n'
            f'{IDENT}' f'instance_id={self.instance_id}\n'
            f')'
        )
    
    def __format__(self, f_spec: str) -> str:
        match f_spec:
            case '':
                return str(self)

            case 'detailed':
                return (
                    f'Savepoint at index {self.index} '
                    f'for iterator instance '
                    f'#{self.instance_id}.'
                )
            
            case 'short': # inspired by C++ repr
                return f'*Iterator[{self.index}]'

            case 'idx' | 'index':
                return f'index {self.index}'
            
            case 'id' | 'instance_id':
                return f'instance ID #{self.instance_id}'
            
            case _:
                raise ValueError(
                    f"Invalid format specifier: '{f_spec}'. "
                    f"Valid options are: `detailed`, `short`, `index` and `instance_id`."
                )


    # ==================================================
    # Conversion
    # ==================================================

    def __hash__(self) -> int:
        return hash( (self.index, self.instance_id) )
    
    def __int__(self) -> int:       return self.index
    def __float__(self) -> float:   return float(self.index)
    def __bool__(self) -> bool:     return self.index > 0


    # ==================================================
    # Logic
    # ==================================================

    def __eq__(self, other: Savepoint | Iterator | int | tuple[int, int]) -> bool:
        match other:
            case Savepoint():
                return (
                    self.index == other.index
                    and
                    self.instance_id == other.instance_id
                )
            
            case Iterator():
                return (
                    self.index == other.index
                    and
                    self.instance_id == id(other)
                )
            
            case int():
                return self.index == other
            
            case (index, instance_id):
                return (
                    self.index == index
                    and
                    self.instance_id == instance_id
                )
            
            case _:
                return False

    def __lt__(self, other: Savepoint | Iterator | int | tuple[int, int]) -> bool:
        match other:
            case Savepoint():
                return self.index < other.index
            
            case Iterator():
                return self.index < other.index
            
            case int():
                return self.index < other
            
            case (index, _):
                return self.index < index
            
            case _:
                raise NotImplementedError(f"Cannot compare Savepoint with {type(other).__name__}.")


class Iterator[I](IteratorBase):
    __slots__ = ('__collection', '__index', '__begin_point')

    def __init__(self, collection: Sequence[I]) -> None:
        self.__collection: list[I] = list(collection)
        self.__index: int = 0
        self.__begin_point: int | None = None

        self.begin()


    # ==================================================
    # Representation
    # ==================================================

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( {len(self)} total items, {self.remaining} remaining )'

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'{IDENT}' f'collection={self.__collection!r},\n'
            f'{IDENT}' f'length={len(self)},\n'
            f'{IDENT}' f'index={self.__index},\n'
            f'{IDENT}' f'remaining={self.remaining}\n'
            f')'
        )


    # ==================================================
    # Iterable Protocol
    # ==================================================

    def __iter__(self) -> Iterator[I]:
        return self
    
    def __next__(self) -> I:
        if self.__index >= len(self):
            raise StopIteration(NO_MORE_ITEMS_ERROR)
        return self.next()


    # ==================================================
    # Operations
    # ==================================================

    def __eq__(self, other: Sequence[I] | Iterator[I]) -> bool:
        if isinstance(other, Iterator):
            return self.__collection == other.remaining_items
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes)):
            return self.__collection == list(other)
        return False
    
    # ==================================================
    # Meta Methods
    # ==================================================

    def __len__(self) -> int:
        return len(self.__collection)


    # ==================================================
    # Conditions
    # ==================================================

    def is_empty(self) -> bool:
        return len(self) == 0
    
    def has_next(self) -> bool:
        return self.__index < len(self)
    

    # ==================================================
    # Operations & Logic
    # ==================================================

    def copy(self) -> Iterator[I]:
            return Iterator(self.__collection)
    
    def _adder(this_coll: list[I], other_coll: I | Sequence[I] | Iterator[I]) -> list[I]:
        match other_coll:
            case Iterator():
                this_coll.extend(other_coll.remaining_items)
            case Sequence() if not isinstance(other_coll, (str, bytes)):
                this_coll.extend(other_coll)
            case _:
                this_coll.append(other_coll)
        
        return this_coll

    def append(self, item: I) -> None:
        self.__collection.append(item)

    def __add__(self, other: I | Sequence[I] | Iterator[I]) -> Iterator[I]:
        new_collection: list[I] = self._adder(
            this_coll  = self.__collection.copy(),
            other_coll = other
        )
        return Iterator(new_collection)

    def __iadd__(self, other: I | Sequence[I] | Iterator[I]) -> Iterator[I]:
        self._adder(
            this_coll  = self.__collection,
            other_coll = other
        )
        return self

    def sort[F: Callable[[I], bool]](self, *, key: F | None = None, reverse: bool = False) -> None:
        self.__collection.sort( key=key, reverse=reverse )


    
    # ==================================================
    # Positioning
    # ==================================================

    def savepoint(self) -> Savepoint:
        savepoint: Savepoint = Savepoint(self.__index, id(self))
        return savepoint

    def __getitem__(self, index: int) -> Savepoint:
        if index < 0 or index >= len(self):
            raise IndexOutOfBoundsError(
                operation   = '__getitem__()',
                index       = index,
                coll_length = len(self)
            )
        return Savepoint(index, id(self))

    def peek(self) -> I:
        if self.__index >= len(self):
            raise StopIteration(NO_MORE_ITEMS_ERROR)
        
        return self.__collection[self.__index]

    def next(self) -> I:
        if not self.has_next():
            raise StopIteration(NO_MORE_ITEMS_ERROR)

        item = self.__collection[self.__index]
        self.__index += 1
        return item

    def back(self) -> I:
        if self.__index <= 0:
            raise InvalidIteratorStateError( operation='back()', required='next()' )
        
        self.__index -= 1
        return self.__collection[self.__index]

    def __rshift__(self, steps: int) -> Iterator[I]:
        if steps < 0:
            raise ValueError("Steps must be a non-negative integer.")
        if self.__index + steps > len(self):
            raise StopIteration(NO_MORE_ITEMS_ERROR)
        
        self.__index += steps
        return self

    def __lshift__(self, steps: int) -> Iterator[I]:
        if steps < 0:
            raise ValueError("Steps must be a non-negative integer.")
        if (idx := self.__index - steps) < 0:
            raise IndexOutOfBoundsError(
                operation   = '__lshift__()',
                index       = idx,
                coll_length = len(self)
            )
        
        self.__index -= steps
        return self


    # ==================================================
    # Fallback Logic
    # ==================================================

    def begin(self) -> None:
        self.__begin_point = self.__index

    def commit(self) -> None:
        self.__begin_point = None

    def rollback(self) -> None:
        if self.__begin_point is None:
            raise InvalidIteratorStateError( operation='rollback()', required='rollback_to()')
        
        self.__index = self.__begin_point

    def rollback_to(self, savepoint: Savepoint) -> None:
        if savepoint.instance_id != id(self):
            raise SavepointIdMismatchError(savepoint.index, self)
        if savepoint.index > self.__index:
            raise InvalidIteratorStateError( operation='rollback_to()', required='rollback()')
        
        self.__index = savepoint.index


    # ==================================================
    # Properties
    # ==================================================

    @property
    def current(self) -> I:
        if self.__index <= 0:
            raise IterationNotStartedError(self)
        if self.__index >= len(self.__collection):
            raise IndexOutOfBoundsError( operation='current()', index=self.__index, coll_length=len(self.__collection) )
        
        return self.__collection[self.__index - 1]

    @property
    def size(self) -> int:
        return len(self)

    @property
    def index(self) -> int:
        return self.__index

    @property
    def remaining(self) -> int:
        return len(self) - self.__index
    
    @property
    def remaining_items(self) -> list[I]:
        return self.__collection[self.__index:].copy()
