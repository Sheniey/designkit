
from typing import Hashable
from collections import deque

from designkit.behavioral.cache.exceptions import ItemNotHashableError
from designkit.behavioral.cache.models import _MISSING, AbstractCache


class FIFOCache[T](AbstractCache[T]):
    def __init__(self, capacity: int) -> None:
        self.__capacity: int = capacity
        self.__map: deque[tuple[Hashable, T]] = deque(maxlen=capacity)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( capacity={self.__capacity} )'

    def __repr__(self) -> str:
        fmt = lambda k, v: f'[{k}:{v}]'
        return ''.join(fmt(k, v) for k, v in self.__map)

    def __getitem__(self, key: Hashable) -> T:
        return self.get(key, _MISSING)

    def __setitem__(self, key: Hashable, value: T) -> None:
        self.put(key, value)

    def __contains__(self, key: Hashable) -> bool:
        return any(k == key for k, _ in self.__map)

    def __len__(self) -> int:
        return len(self.__map)

    def get(self, key: Hashable, default: T | object = _MISSING) -> T | object:
        for k, v in self.__map:
            if k == key:
                return v
        return default

    def put(self, key: Hashable, value: T) -> None:
        try:
            for i, (k, _) in enumerate(self.__map):
                if k == key:
                    del self.__map[i]
                    break
            self.__map.append((key, value))
        except TypeError:
            raise ItemNotHashableError(self.__class__.__name__, key)

    def dump(self, from_page: int = 0, to_page: int | None = None) -> list[tuple[Hashable, T]]:
        PAGE_SIZE: int = 32
        
        if to_page is None:
            to_page = len(self.__map)
        
        if from_page < 0 or to_page < 0 or from_page >= to_page:
            raise ValueError(f'Invalid page range: from_page={from_page}, to_page={to_page}')
        
        start_index: int = from_page * PAGE_SIZE
        end_index: int = min(to_page * PAGE_SIZE, len(self.__map))
        return list(self.__map)[start_index:end_index]

    def clear(self) -> None:
        self.__map.clear()

    def copy(self) -> FIFOCache[T]:
        new_cache: FIFOCache[T] = FIFOCache(self.__capacity)
        new_cache.__map = self.__map.copy()
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
