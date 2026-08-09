
class CacheException(Exception):
    """Base class for cache-related exceptions."""
    pass

class ItemNotHashableError(CacheException):
    """Raised when an item is not hashable."""
    def __init__(self, cache: str, key: object) -> None:
        self.cache = cache
        self.key = key
        super().__init__(f'The {self.cache} key must be hashable but got "{self.key}", implement `.__hash__()` method.')
