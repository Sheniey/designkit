
class Node[T]:
    def __init__(self, key: str, value: T) -> None:
        self.key: str = key
        self.value: T = value
        self.prev: Node[T] | None = None
        self.next: Node[T] | None = None

class LRUCache[T]:
    def __init__(self, capacity: int) -> None:
        self.__capacity: int = capacity
        self.__map: dict[str, Node[T]] = {}
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

    def __getitem__(self, key: str) -> T:
        return self.get(key)

    def __setitem__(self, key: str, value: T) -> None:
        self.put(key, value)

    def __contains__(self, key: str) -> bool:
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
    
    def get(self, key: str) -> T:
        node: Node[T] | None = self.__map.get(key)

        if node is None:
            return -1
        
        self._remove(node)
        self._add_to_front(node)
        
        return node.value

    def put(self, key: str, value: T) -> None:
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

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def free_space(self) -> int:
        return self.__capacity - len(self.__map)

    @property
    def is_full(self) -> bool:
        return len(self.__map) >= self.__capacity
