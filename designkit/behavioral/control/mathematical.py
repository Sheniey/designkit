
from typing import Never
from dataclasses import dataclass


# ==================================================
# Abstract Base Classes
# ==================================================

class EitherResponse[L, R]:
    pass


# ==================================================
# Result Types
# ==================================================

@dataclass(frozen=True)
class Left[T](EitherResponse[T, Never]):
    __match_args__ = ('value',)

    value: T


@dataclass(frozen=True)
class Right[T](EitherResponse[Never, T]):
    __match_args__ = ('value',)

    value: T



# ==================================================
# Type Aliases
# ==================================================

type Either[L, R] = Left[L] | Right[R]
