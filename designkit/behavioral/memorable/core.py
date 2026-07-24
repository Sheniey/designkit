
from dataclasses import dataclass, field
from typing import Deque as _Deque
from collections import deque as _deque
import heapq as _heapq
from designkit_utils.docs import BigO, complexity

from .exceptions import (
    StackEmptyError, QueueEmptyError, DequeEmptyError, HeapEmptyError,
    StackFullError, QueueFullError, DequeFullError, HeapFullError
)



@dataclass
class Stack[T]:
    capacity: int | None = None
    memory: _Deque[T] = field(default_factory=_deque, init=False)

    @complexity( time=BigO.CONSTANT, space=BigO.LINEAR )
    def push(self, item: T) -> None:
        if self.full:
            raise StackFullError()
        
        self.memory.append(item)

    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def pop(self) -> T:
        if self.empty:
            raise StackEmptyError()
        
        return self.memory.pop()

    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def peek(self) -> T:
        if self.empty:
            raise StackEmptyError()
        
        return self.memory[-1]
    
    @property
    def full(self) -> bool:
        return self.capacity is not None and len(self.memory) >= self.capacity
    
    @property
    def empty(self) -> bool:
        return not self.memory




@dataclass
class Queue[T]:
    capacity: int | None = None
    memory: _Deque[T] = field(default_factory=_deque, init=False)

    @complexity( time=BigO.LINEAR, space=BigO.LINEAR )
    def enqueue(self, item: T) -> None:
        if self.full:
            raise QueueFullError()
        
        self.memory.append(item)

    @complexity( time=BigO.LINEAR, space=BigO.CONSTANT )
    def dequeue(self) -> T:
        if self.empty:
            raise QueueEmptyError()
        
        return self.memory.pop(0)

    @property
    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def front(self) -> T:
        if self.empty:
            raise QueueEmptyError()
        
        return self.memory[0]
    
    @property
    def full(self) -> bool:
        return self.capacity is not None and len(self.memory) >= self.capacity

    @property
    def empty(self) -> bool:
        return not self.memory



@dataclass
class Deque[T]:
    capacity: int | None = None
    memory: _Deque[T] = field(default_factory=_deque, init=False)

    def _full_checker(self, func):
        def decorator(*args, **kwargs):
            if self.full:
                raise DequeFullError()
            return func(*args, **kwargs)
        return decorator

    def _empty_checker(self, func):
        def decorator(*args, **kwargs):
            if self.empty:
                raise DequeEmptyError()
            return func(*args, **kwargs)
        return decorator

    @complexity( time=BigO.LINEAR, space=BigO.LINEAR )
    @_empty_checker
    def push_front(self, item: T) -> None:
        if self.full:
            raise DequeFullError()
        
        self.memory.appendleft(item)

    @complexity( time=BigO.LINEAR, space=BigO.LINEAR )
    def push_back(self, item: T) -> None:
        if self.full:
            raise DequeFullError()
        
        self.memory.append(item)

    @complexity( time=BigO.LINEAR, space=BigO.CONSTANT )
    def pop_front(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory.popleft()

    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def pop_back(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory.pop()

    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def peek_front(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory[0]
    
    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def peek_back(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory[-1]

    @property
    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def front(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory[0]
    
    @property
    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def back(self) -> T:
        if self.empty:
            raise DequeEmptyError()
        
        return self.memory[-1]
    
    @property
    def full(self) -> bool:
        return self.capacity is not None and len(self.memory) >= self.capacity

    @property
    def empty(self) -> bool:
        return not self.memory




@dataclass
class Heap[T]:
    capacity: int | None = None
    memory: _Deque[T] = field(default_factory=_deque, init=False)

    @complexity( time=BigO.LINEAR, space=BigO.LINEAR )
    def push(self, item: T) -> None:
        if self.full:
            raise HeapFullError()
        
        _heapq.heappush(self.memory, item)
    
    @complexity( time=BigO.LINEAR, space=BigO.CONSTANT )
    def pop(self) -> T:
        if self.empty:
            raise HeapEmptyError()
        
        return _heapq.heappop(self.memory)

    @complexity( time=BigO.CONSTANT, space=BigO.CONSTANT )
    def peek(self) -> T:
        if self.empty:
            raise HeapEmptyError()
        
        return self.memory[0]

    @property
    def full(self) -> bool:
        return self.capacity is not None and len(self.memory) >= self.capacity

    @property
    def empty(self) -> bool:
        return not self.memory
