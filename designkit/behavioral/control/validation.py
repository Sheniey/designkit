
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


# Example Usage:

db: list[int] = [-3, 0, 5, 10, -62, 13, 2]

def are_all_positive(n: list[int]) -> bool:
    return all(x > 0 for x in n)

def validate_db() -> Validated[list[int]]:
    return Validation.validate(db, are_all_positive)

results: Validated[list[int]] = validate_db()

match results:
    case Valid(value=numbers):
        print(f"All numbers are valid: {numbers}")
    case Invalid(value=numbers):
        print(f"Few numbers are invalid: {numbers}")
