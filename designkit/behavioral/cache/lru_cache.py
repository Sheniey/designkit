
from typing import Hashable

from designkit.behavioral.cache.exceptions import ItemNotHashableError
from designkit.behavioral.cache.models import _MISSING, AbstractCache

class Node[T]:
    def __init__(self, key: Hashable, value: T) -> None:
        self.key: Hashable = key
        self.value: T = value
        self.prev: Node[T] | None = None
        self.next: Node[T] | None = None

class LRUCache[T](AbstractCache[T]):
    def __init__(self, capacity: int) -> None:
        self.__capacity: int = capacity
        self.__map: dict[Hashable, Node[T]] = {}
        self.__head: Node[T] = Node('', 0)  # type: ignore
        self.__tail: Node[T] = Node('', 0)  # type: ignore
        self.__head.next = self.__tail
        self.__tail.prev = self.__head

    def __repr__(self) -> str:
        nodes: list[str] = []
        current: Node[T] | None = self.__head.next

        while current is not None and current != self.__tail:
            nodes.append(f'({current.key}: {current.value})')
            current = current.next
        
        return ' <-> '.join(nodes)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( capacity={self.__capacity}, map={self.__map} )'

    def __getitem__(self, key: Hashable) -> T:
        return self.get(key)

    def __setitem__(self, key: Hashable, value: T) -> None:
        self.put(key, value)

    def __contains__(self, key: Hashable) -> bool:
        try:
            hash(key)
        except TypeError:
            raise ItemNotHashableError(self.__class__.__name__, key)
            
        return key in self.__map

    def __len__(self) -> int:
        return len(self.__map)
    
    def _remove(self, node: Node[T]) -> None:
        if node.prev is not None:
            node.prev.next = node.next

        if node.next is not None:
            node.next.prev = node.prev
    
    def _add_to_front(self, node: Node[T]) -> None:
        node.next = self.__head.next
        node.prev = self.__head
        self.__head.next.prev = node
        self.__head.next = node
    
    def get(self, key: Hashable, default: T | object = _MISSING) -> T | object:
        node: Node[T] | None = self.__map.get(key)

        if node is None:
            return default
        
        self._remove(node)
        self._add_to_front(node)
        
        return node.value

    def put(self, key: Hashable, value: T) -> None:
        existing: Node[T] | None = self.__map.get(key)

        if existing is not None:
            existing.value = value
            self._remove(existing)
            self._add_to_front(existing)
            return
        
        node: Node[T] = Node(key, value)
        self.__map[key] = node

        self._add_to_front(node)

        if len(self.__map) > self.__capacity:
            lru: Node[T] | None = self.__tail.prev

            if lru is not None:
                self._remove(lru)
                del self.__map[lru.key]

    def dump(self, from_page: int = 0, to_page: int | None = None) -> list[tuple[Hashable, T]]:
        PAGE_SIZE: int = 32

        if to_page is None:
            to_page = len(self.__map)

        if from_page < 0 or to_page < 0 or from_page >= to_page:
            raise ValueError(f'Invalid page range: from_page={from_page}, to_page={to_page}')

        nodes: list[tuple[Hashable, T]] = []
        current: Node[T] | None = self.__head.next
        index: int = 0

        while current is not None and current != self.__tail:
            if index >= from_page * PAGE_SIZE and index < to_page * PAGE_SIZE:
                nodes.append((current.key, current.value))
            elif index >= to_page * PAGE_SIZE:
                break

            current = current.next
            index += 1
        return nodes

    def clear(self) -> None:
        self.__map.clear()
        self.__head.next = self.__tail
        self.__tail.prev = self.__head

    def copy(self) -> LRUCache[T]:
        new_cache: LRUCache[T] = LRUCache(self.__capacity)
        current: Node[T] | None = self.__head.next

        while current is not None and current != self.__tail:
            new_cache.put(current.key, current.value)
            current = current.next
        
        return new_cache

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def free_space(self) -> int:
        return self.__capacity - len(self.__map)

    @property
    def is_full(self) -> bool:
        return len(self.__map) >= self.__capacity
