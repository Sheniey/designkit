
from typing import Any, Callable
from dataclasses import dataclass
import inspect

@dataclass
class DecorableInfo:
    optional: bool = False
    async_: bool = False
    cache: bool = False
    trace: bool = False
    lock: bool = False

def decorable[F: Callable[..., Any]](
        func: F | None = None,
        *,
        optional: bool = False,
        async_: bool = False,
        cache: bool = False,
        trace: bool = False,
        lock: bool = False
    ) -> Callable:
    
    def wrapper(fn: F) -> F:
        fn.__decorable__ = DecorableInfo(
            optional=optional,
            async_=async_,
            cache=cache,
            trace=trace,
            lock=lock
        )
        return fn

    if func is None:
        return wrapper

    return wrapper(func)

def component(cls: type) -> type:
    cls.__decorables__ = {
        k: v.__decorable__
        for k, v in cls.__dict__.items()
        if hasattr(v, '__decorable__')
    }
    cls.__name__ = cls.__name__
    return cls

def decorator_of[C](component: C) -> Callable[[type], type]:
    def wrapper(cls: type) -> type:
        if not hasattr(component, '__init__'):
            raise TypeError(f"'{component.__name__}' does not have an __init__ method")
        
        # inspects if at least one parameter has the <component> type
        constructor_params: dict[str, inspect.Parameter] = inspect.signature(cls.__init__).parameters
        param_types: set[type] = {param.annotation for param in constructor_params.values() if param.annotation is not inspect.Parameter.empty}
        if component not in param_types:
            raise TypeError(f"'{cls.__name__}' must have a parameter of type '{component.__name__}' in its constructor")

        if not hasattr(component, '__decorables__'):
            raise TypeError(f"'{component.__name__}' is not a valid component class")
        
        decorables: list[tuple[str, DecorableInfo]] = list(getattr(component, '__decorables__').items())
        for decorable in decorables: 
            name, info = decorable
            if not hasattr(cls, name):
                if info.optional:
                    continue
                raise TypeError(f"'{cls.__name__}' must implement the decorable method '{name}' from '{component.__name__}'")

        cls.__component__ = component

        return cls
    
    return wrapper
