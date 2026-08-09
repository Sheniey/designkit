
import re
from designkit.behavioral.typing import Assertion, classname
from designkit.creational.types.dtypes.money import currency_symbols
from typing import Any, Self, Literal

from designkit.creational.types.utils import Numeric, DType, parser_cache

# This matches... x1, x1.0, 4.000, 7, 32.00, etc. It does not match x1.0000, 1.0000, 1.00000, etc.
# IMPORTANT: there is a space at the /start/ and the /end/ to block false positives like "$100.00" or "8.00%"
pattern: re.Pattern = re.compile(r'(?<![-' + re.escape(currency_symbols) + r'])x?(?P<quantity>0|[1-9][0-9]*)(?:\.0{1,3})?(?![%\d\.])', re.VERBOSE)

def validate_quantity(value: int, father: str = 'Quantity') -> None:
    if value < 0:
        raise ValueError(f'{father} must be non-negative, got {value}')

@parser_cache()
def parse_quantity(value: str | int | Quantity, father: str) -> int:
    match value:
        case str():
            match = pattern.search(value)
            if not match:
                raise ValueError(f'{father} can be a str but must look like "x1.00", "24.000", or "64", got {value}')
            return int(match.group('quantity'))

        case int():
            validate_quantity(value, father)
            return value

        case Quantity():
            return value.value

        case _:
            raise TypeError(f'{father} must be a str, int, or Quantity but got {classname(value)}')

fmt_value = lambda value: f'{value}.000'

class Quantity(DType):
    def __init__(self, value: str | int) -> None:
        self.__value: int = parse_quantity(value, classname(self))
        self.__fmt_value: str = fmt_value(self.__value)

    def __str__(self) -> str:
        return self.__fmt_value

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__fmt_value} units)'

    def __format__(self, format_spec: str | Literal['value', 'formal', 'by', 'x']) -> str:
        match format_spec:
            case 'value':
                return self.__value
            case 'formal':
                return f'{self.__fmt_value} units'
            case 'by'|'x':
                return f'x{self.__fmt_value}'
            case _:
                return f'{self.__fmt_value:{format_spec}}'
    
    def __int__(self) -> int:
        return self.__value

    def __float__(self) -> float:
        return float(self.__value)

    def __add__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value + other_value)

    def __radd__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value + self.__value)

    def __iadd__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        possible_value = self.__value + other_value
        validate_quantity(possible_value, classname(self))
        self.__value = possible_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __sub__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value - other_value)

    def __rsub__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value - self.__value)

    def __isub__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        possible_value = self.__value - other_value
        validate_quantity(possible_value, classname(self))
        self.__value = possible_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __mul__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value * other_value)

    def __rmul__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value * self.__value)

    def __imul__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value *= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __truediv__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value // other_value)

    def __rtruediv__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value // self.__value)

    def __itruediv__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        possible_value = self.__value // other_value
        validate_quantity(possible_value, classname(self))
        self.__value = possible_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __mod__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value % other_value)

    def __rmod__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value % self.__value)

    def __imod__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value %= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __pow__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value ** other_value)

    def __rpow__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value ** self.__value)

    def __ipow__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value **= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __rshift__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value >> other_value)

    def __rrshift__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value >> self.__value)

    def __irshift__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value >>= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __lshift__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(self.__value << other_value)

    def __rlshift__(self, other: str | int | Quantity) -> Quantity:
        other_value: int = parse_quantity(other, classname(self))
        return Quantity(other_value << self.__value)

    def __ilshift__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        possible_value = self.__value << other_value
        validate_quantity(possible_value, classname(self))
        self.__value = possible_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __bool__(self) -> bool:
        return self.__value != 0

    def __eq__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value == other_value

    def __ne__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value != other_value

    def __and__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value & other_value

    def __rand__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return other_value & self.__value

    def __iand__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value &= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __or__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value | other_value

    def __ror__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return other_value | self.__value

    def __ior__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value |= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __xor__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value ^ other_value

    def __rxor__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return other_value ^ self.__value

    def __ixor__(self, other: str | int | Quantity) -> Self:
        other_value: int = parse_quantity(other, classname(self))
        self.__value ^= other_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def __gt__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value > other_value

    def __ge__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value >= other_value

    def __lt__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value < other_value

    def __le__(self, other: str | int | Quantity) -> bool:
        other_value: int = parse_quantity(other, classname(self))
        return self.__value <= other_value

    def __pos__(self) -> Quantity:
        return Quantity(self.__value)

    def __neg__(self) -> Quantity:
        raise ValueError(f'{classname(self)} cannot be negative, got {self.__value}')

    def __invert__(self) -> Quantity:
        return Quantity(~self.__value)

    def __abs__(self) -> Quantity:
        return Quantity(abs(self.__value))

    def __hash__(self) -> int:
        return hash(self.__value)

    def __copy__(self) -> Quantity:
        return Quantity(self.__value)

    @staticmethod
    def validate(value: str | int | Quantity) -> bool:
        try:
            value = parse_quantity(value, 'value')
            validate_quantity(value, 'Quantity')
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def parse(cls, value: str | int | Quantity) -> Quantity:
        value = parse_quantity(value, classname(cls))
        validate_quantity(value, classname(cls))
        return cls(value)

    @classmethod
    def findall(cls, text: str) -> list[Quantity]:
        matches = pattern.findall(text)
        return [cls(int(match)) for match in matches]

    def increment(self, units: int = 1) -> Self:
        Assertion(units).must_be(int)

        self.__value += units
        self.__fmt_value = fmt_value(self.__value)
        return self

    def decrement(self, units: int = 1) -> Self:
        Assertion(units).must_be(int)
        possible_value = self.__value - units
        validate_quantity(possible_value, classname(self))
        self.__value = possible_value
        self.__fmt_value = fmt_value(self.__value)
        return self

    def copy(self) -> Quantity:
        return Quantity(self.__value)

    @property
    def value(self) -> int:
        return self.__value

    @property
    def quantity(self) -> int:
        return self.__value
