
from functools import wraps
from typing import Callable, overload, Any

from .models import _MISSING, AbstractCache
from .lru_cache import LRUCache


@overload
def cached[F: Callable[..., R], R](func: F, /) -> F: ...


@overload
def cached[F: Callable[..., R], R](
    func: None = None,
    /,
    *,
    capacity: int = 32,
    cache: type[AbstractCache[R]] = LRUCache,
    skip_when: Callable[[tuple[Any], dict[str, Any]], bool] = lambda args, kwargs: False,
) -> Callable[[F], F]: ...

def cached[F: Callable[..., R], R](
    func: None = None,
    /,
    *,
    capacity: int = 32,
    cache: type[AbstractCache[R]] = LRUCache,
    skip_when: Callable[[tuple[Any], dict[str, Any]], bool] = lambda args, kwargs: False,
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if skip_when(*args, **kwargs):
                return func(*args, **kwargs)

            key: tuple[tuple, tuple[tuple[str, object]]] = (args, tuple(sorted(kwargs.items())))
            cache_result: R | None = wrapper.cache.get(key)
            if cache_result is not _MISSING:
                return cache_result

            result: R = func(*args, **kwargs)
            wrapper.cache.put(key, result)
            return result

        wrapper.cache = cache[R](capacity)
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
