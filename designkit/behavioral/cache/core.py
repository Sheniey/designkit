
from functools import wraps
from typing import Callable

from .models import AbstractCache
from .lru_cache import LRUCache


def cached[F: Callable[..., R], R](capacity: int, cache: AbstractCache[R] = LRUCache) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key: tuple[tuple, tuple[tuple[str, object]]] = (args, tuple(sorted(kwargs.items())))
            if key in wrapper.cache:
                return wrapper.cache.get(key)
            
            result: R = func(*args, **kwargs)
            wrapper.cache.put(key, result)
            return result

        wrapper.cache = cache[R](capacity)
        return wrapper
    return decorator
