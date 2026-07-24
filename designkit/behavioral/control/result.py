
from dataclasses import dataclass


# ==================================================
# Abstract Base Classes
# ==================================================

class Response[T]:
    def __enter__(self) -> Response[T]:
        return self

    def __exit__[E_T](self, exc_type: E_T, exc_value, traceback) -> Err[E_T] | None:
        if exc_type is not None:
            return Err(exc_value)
        return None
    
    @staticmethod
    def is_optional(value: Result | Maybe | None) -> bool:
        return isinstance(value, Maybe) or value is None
    
    @staticmethod
    def is_success(value: Result | Maybe) -> bool:
        return not isinstance(value, Err)


# ==================================================
# Result Types
# ==================================================

@dataclass(frozen=True)
class Ok[T](Response[T]):
    __match_args__ = ('value',)

    value: T


@dataclass(frozen=True)
class Err[T](Response[T]):
    __match_args__ = ('error',)

    error: T


@dataclass(frozen=True)
class Some[T](Response[T]):
    __match_args__ = ('value',)

    value: T


@dataclass(frozen=True)
class Nothing(Response[None]):
    pass



# ==================================================
# Type Aliases
# ==================================================

type Result[T, E] = Ok[T] | Err[E]
type Maybe[T] = Some[T] | Nothing
