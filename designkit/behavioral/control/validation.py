
from dataclasses import dataclass
from typing import Never, Callable
from inspect import isawaitable


# ==================================================
# Abstract Validation Class
# ==================================================

class ValidatedResponse[V, I]: # T:True, F:False
    def is_valid(self) -> bool:
        return isinstance(self, Valid)

    def is_invalid(self) -> bool:
        return isinstance(self, Invalid)

class Validation[T]:
    @staticmethod
    def validate(value: T, validator: Callable[[T], bool]) -> ValidatedResponse[T, T]:
        validity: bool = bool(validator(value))
        match validity:
            case True:
                return Valid(value=value)
            case False:
                return Invalid(value=value)

    @staticmethod
    async def validate_async(value: T, validator: Callable[[T], bool]) -> ValidatedResponse[T, T]:
        result = validator(value)
        if isawaitable(result):
            result = await result
        validity: bool = bool(result)

        match validity:
            case True:
                return Valid(value=value)
            case False:
                return Invalid(value=value)



# ==================================================
# Validation Types
# ==================================================

@dataclass(frozen=True)
class Valid[T](ValidatedResponse[T, Never]):
    __match_args__ = ('value',)

    value: T


@dataclass(frozen=True)
class Invalid[T](ValidatedResponse[Never, T]):
    __match_args__ = ('value',)

    value: T


# ==================================================
# Type Aliases
# ==================================================

type Validated[T] = Valid[T] | Invalid[T]

