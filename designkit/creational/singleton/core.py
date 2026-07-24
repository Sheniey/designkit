
from typing import Any, Callable
from collections import defaultdict
from inspect import isclass

from .exceptions import ItsNotAClassError

def singleton(cls) -> Callable[..., Any]:
    """
    *"Transforms a class into a singleton."*
    
    A singleton is a design pattern that restricts the instantiation of a class to one single instance and provides a global point of access to that instance. This decorator ensures that only one instance of the decorated class can be created, and subsequent calls to create an instance will return the same instance.

    Example:
        >>> @singleton
        >>> class MyClass:
            ... pass
        >>> 
        >>> a = MyClass()
        >>> b = MyClass()
        >>> assert a is b  # True

    Args:
        cls: The class to be transformed into a singleton.
    
    Returns:
        A function that returns the singleton instance of the class.
    """
    instances: defaultdict[type, object] = defaultdict(lambda: None)

    def wrapper(*args: Any, **kwargs: Any) -> object:
        if not isclass(cls):
            raise ItsNotAClassError(cls)
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
