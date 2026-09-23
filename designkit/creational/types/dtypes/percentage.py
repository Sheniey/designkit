
import re
from decimal import Decimal
from typing import Self, Literal

from designkit.behavioral.typing import Assertion, classname
from designkit.creational.types.utils import Numeric, DType, parser_cache


soft_pattern: re.Pattern = re.compile(r'[+-]?(0?(\.|,))?(\d+(?:(\.|,)\d+)?)\s?%?')
explicit_pattern: re.Pattern = re.compile(r'[+-]?(0(\.|,))?(\d+(?:(\.|,)\d+)?)%')

@parser_cache()
def parse_percentage(value: str | Numeric | Percentage, father: str) -> tuple[Decimal, type]:
    match value:
        case str():
            value = value.strip() # x % -> x.x%

            if value.endswith('%'): # x% -> x
                value = value[:-1]

            value = value.replace(',', '.') # ,x -> .x
            return Decimal(value), str
        
        case int():
            return Decimal(value), int

        case float():
            return Decimal(str(value)), float

        case Decimal():
            return value, Decimal
        
        case Percentage():
            return value.value, Percentage
        
        case _:
            raise TypeError(f'{father} must be a str, int, float, Decimal or Percentage but got {classname(value)}')

def verify_limits(value: Decimal, limits: tuple[Decimal, Decimal] | None, father: str) -> None:
    if limits is not None:
        min_limit, max_limit = limits
        Assertion(min_limit).must_be(Decimal)
        Assertion(max_limit).must_be(Decimal)

        if min_limit > max_limit:
            raise ValueError(f'Min limit {min_limit} cannot be greater than max limit {max_limit}')

        if not (min_limit <= value <= max_limit):
            raise ValueError(f'{father} must be between {min_limit} and {max_limit} but got {float(value)}')

class Percentage(DType):
    RANGE_N100_TO_P100: tuple[Decimal, Decimal] | None = (Decimal('-100.0'), Decimal('100.0'))
    RANGE_0_TO_100:     tuple[Decimal, Decimal] | None = (Decimal('0.0'), Decimal('100.0'))
    RANGE_UNLIMITED:    tuple[Decimal, Decimal] | None = None

    def __init__(self, value: str | Numeric, *, limits: tuple[Decimal, Decimal] | None = RANGE_UNLIMITED) -> None:
        self.__value: Decimal = parse_percentage(value, classname(self))[0]
        self.__limits: tuple[Decimal, Decimal] | None = limits

        verify_limits(self.__value, self.__limits, classname(self))

    def __format__(self, format_spec: str = '.2f') -> str:
        match format_spec:
            case '':
                return f'{self.__value:.2f}%'
            case 'short':
                return f'{self.__value:.0f}%'
            case 'full':
                return f'{self.__value}%'
            case _:
                return f'{self.__value:{format_spec}}%'

    def __str__(self) -> str:
        return f'{self.__value:.2f}%'

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value:.2f}%)'
    
    def __add__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(self.__value + other_value, limits=self.__limits)

    def __radd__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(other_value + self.__value, limits=self.__limits)
            
    def __iadd__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value + other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self

    def __sub__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(self.__value - other_value, limits=self.__limits)

    def __rsub__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(other_value - self.__value, limits=self.__limits)
        
    def __isub__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value - other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self
            
    def __mul__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, dtype = parse_percentage(other, 'other')

        new_value: Decimal
        if dtype is Percentage:
            new_value = self.__value * (other_value / Decimal(100))
        else:
            new_value = self.__value * other_value

        return Percentage(new_value, limits=self.__limits)

    def __rmul__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, dtype = parse_percentage(other, 'other')

        new_value: Decimal
        if dtype is Percentage:
            new_value = other_value * (self.__value / Decimal(100))
        else:
            new_value = other_value * self.__value

        return Percentage(new_value, limits=self.__limits)
      
    def __imul__(self, other: str | Numeric | Percentage) -> Self:
        other_value, dtype = parse_percentage(other, 'other')

        new_value: Decimal
        if dtype is Percentage:
            new_value = self.__value * (other_value / Decimal(100))
        else:
            new_value = self.__value * other_value

        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self
    
    def __truediv__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, dtype = parse_percentage(other, 'other')
        if other_value == 0:
            raise ZeroDivisionError(f'Cannot calculate a division with "other" being zero, raise division by zero')

        new_value: Decimal
        if dtype is Percentage:
            new_value = self.__value / (other_value / Decimal(100))
        else:
            new_value = self.__value / other_value

        return Percentage(new_value, limits=self.__limits)

    def __rtruediv__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, dtype = parse_percentage(other, 'other')
        if self.__value == 0:
            raise ZeroDivisionError(f'Cannot calculate a division with "self.value" being zero, raise division by zero')

        new_value: Decimal
        if dtype is Percentage:
            new_value = other_value / (self.__value / Decimal(100))
        else:
            new_value = other_value / self.__value

        return Percentage(new_value, limits=self.__limits)

    def __itruediv__(self, other: str | Numeric | Percentage) -> Self:
        other_value, dtype = parse_percentage(other, 'other')
        if other_value == 0:
            raise ZeroDivisionError(f'Cannot calculate a division with "other" being zero, raise division by zero')

        new_value: Decimal
        if dtype is Percentage:
            new_value = self.__value / (other_value / Decimal(100))
        else:
            new_value = self.__value / other_value

        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self

    def __mod__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        if other_value == 0:
            raise ZeroDivisionError(f'Cannot calculate a modulo with "other" being zero, raise division by zero')

        new_value: Decimal = self.__value % other_value
        return Percentage(new_value, limits=self.__limits)

    def __rmod__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        if self.__value == 0:
            raise ZeroDivisionError(f'Cannot calculate a modulo with "self.value" being zero, raise division by zero')

        new_value: Decimal = other_value % self.__value
        return Percentage(new_value, limits=self.__limits)

    def __imod__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        if other_value == 0:
            raise ZeroDivisionError(f'Cannot calculate a modulo with "other" being zero, raise division by zero')

        new_value: Decimal = self.__value % other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self

    def __pow__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value ** other_value
        return Percentage(new_value, limits=self.__limits)

    def __bool__(self) -> bool:
        return self.__value != 0.0

    def __and__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(self.__value & other_value, limits=self.__limits)

    def __rand__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(other_value & self.__value, limits=self.__limits)

    def __iand__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value & other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self

    def __or__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(self.__value | other_value, limits=self.__limits)

    def __ror__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(other_value | self.__value, limits=self.__limits)
    
    def __ior__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value | other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self

    def __xor__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(self.__value ^ other_value, limits=self.__limits)

    def __rxor__(self, other: str | Numeric | Percentage) -> Percentage:
        other_value, _ = parse_percentage(other, 'other')
        return Percentage(other_value ^ self.__value, limits=self.__limits)

    def __ixor__(self, other: str | Numeric | Percentage) -> Self:
        other_value, _ = parse_percentage(other, 'other')
        new_value: Decimal = self.__value ^ other_value
        verify_limits(new_value, self.__limits, classname(self))
        self.__value = new_value
        return self
    
    def __gt__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value > other_value

    def __ge__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value >= other_value

    def __lt__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value < other_value
    
    def __le__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value <= other_value

    def __eq__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value == other_value

    def __ne__(self, other: str | Numeric | Percentage) -> bool:
        other_value, _ = parse_percentage(other, 'other')
        return self.__value != other_value

    def __invert__(self) -> Percentage:
        return Percentage(~int(self.__value), limits=self.__limits)

    def __neg__(self) -> Percentage:
        return Percentage(-self.__value, limits=self.__limits)

    def __pos__(self) -> Percentage:
        return Percentage(+self.__value, limits=self.__limits)

    def __hash__(self) -> int:
        return hash(self.__value)

    def __int__(self) -> int:
        return int(self.__value)

    def __float__(self) -> float:
        return float(self.__value)

    def __abs__(self) -> Percentage:
        return Percentage(abs(self.__value), limits=self.__limits)

    def __round__(self, ndigits: int = 2) -> Percentage:
        return Percentage(round(self.__value, ndigits), limits=self.__limits)

    def __copy__(self) -> Percentage:
        return Percentage(self.__value, limits=self.__limits)

    @classmethod
    def from_fraction(cls, fraction: float | Decimal) -> Percentage:
        return cls(Decimal(fraction) * Decimal(100))

    def to_fraction(self) -> Decimal:
        return self.__value / Decimal(100)

    @staticmethod
    def validate(value: str | Numeric | Percentage, *, limits: tuple[Decimal, Decimal] | None = RANGE_UNLIMITED) -> bool:
        try:
            x, _ = parse_percentage(value, 'value')
            verify_limits(x, limits, 'Percentage')
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    @parser_cache()
    def parse(cls, value: str | Numeric, mode: Literal['soft', 'explicit'] = 'soft') -> Percentage:
        """
        `Soft` mode matches:
            `50`, `-50`, `+50`, `50%`, `-50%`, `+50%`,
            `3.14`, `-3.14`, `+3.14`, `3.14%`, `-3.14%`, `+3.14%`,
            `3,14`, `-3,14`, `+3,14`, `3,14%`, `-3,14%`, `+3,14%`
            `.20`, `-.20`, `+.20`, `.20%`, `-.20%`, `+.20%`,
            `,20`, `-,20`, `+,20`, `,20%`, `-,20%`, `+,20%`,
            `0.1`, `-0.1`, `+0.1`, `0.1 %`, `-0.1 %`, `+0.1 %`,
            `0,1`, `-0,1`, `+0,1`, `0,1 %`, `-0,1 %`, `+0,1 %`
            `0`, `-0`, `+0`, `0 %`, `-0 %`, `+0 %`
            `50 %`, `-50 %`, `+50 %`,
        
        `Explicit` mode matches:
            `50%`, `-50%`, `+50%`,
            `3.14%`, `-3.14%`, `+3.14%`,
            `3,14%`, `-3,14%`, `+3,14%`,
            `0.20%`, `-0.20%`, `+0.20%`,
            `0,20%`, `-0,20%`, `+0,20%`,
            `0.1%`, `-0.1%`, `+0.1%`
            `0,1%`, `-0,1%`, `+0,1%`
            `0%`, `-0%`, `+0%`
        """
        Assertion(value).must_be(str, int, float, Decimal)

        pattern: re.Pattern
        match mode:
            case 'soft':
                pattern = soft_pattern
            case 'explicit':
                pattern = explicit_pattern
            case _:
                raise ValueError(f'Unknown parsing mode: {mode!r}')

        match = pattern.fullmatch(str(value).strip())
        if not match:
            return None
        return cls(match[0])

    @classmethod
    def findall(cls, text: str, mode: Literal['soft', 'explicit'] = 'soft') -> list[Percentage]:
        """
        `Soft` mode matches:
            `50`, `-50`, `+50`, `50%`, `-50%`, `+50%`,
            `3.14`, `-3.14`, `+3.14`, `3.14%`, `-3.14%`, `+3.14%`,
            `3,14`, `-3,14`, `+3,14`, `3,14%`, `-3,14%`, `+3,14%`
            `.20`, `-.20`, `+.20`, `.20%`, `-.20%`, `+.20%`,
            `,20`, `-,20`, `+,20`, `,20%`, `-,20%`, `+,20%`,
            `0.1`, `-0.1`, `+0.1`, `0.1 %`, `-0.1 %`, `+0.1 %`,
            `0,1`, `-0,1`, `+0,1`, `0,1 %`, `-0,1 %`, `+0,1 %`
            `0`, `-0`, `+0`, `0 %`, `-0 %`, `+0 %`
            `50 %`, `-50 %`, `+50 %`,

        `Explicit` mode matches:
            `50%`, `-50%`, `+50%`,
            `3.14%`, `-3.14%`, `+3.14%`,
            `3,14%`, `-3,14%`, `+3,14%`,
            `0.20%`, `-0.20%`, `+0.20%`,
            `0,20%`, `-0,20%`, `+0,20%`,
            `0.1%`, `-0.1%`, `+0.1%`
            `0,1%`, `-0,1%`, `+0,1%`
            `0%`, `-0%`, `+0%`
        """
        Assertion(text).must_be(str)

        pattern: re.Pattern
        match mode:
            case 'soft':
                pattern = soft_pattern
            case 'explicit':
                pattern = explicit_pattern
            case _:
                raise ValueError(f'Unknown parsing mode: {mode!r}')

        matches = pattern.findall(text)
        if not matches:
            return []
        return [cls(match[0]) for match in matches]

    @staticmethod
    def apply_reduction(value: Numeric, percentage: str | Numeric | Percentage) -> Decimal:
        Assertion(value).must_be(int, float, Decimal)
        Assertion(percentage).must_be(str, int, float, Decimal, Percentage)

        percentage_value, _ = parse_percentage(percentage, 'percentage')
        return Decimal(value) * (1 - (percentage_value / Decimal(100)))

    @staticmethod
    def apply_increase(value: Numeric, percentage: str | Numeric | Percentage) -> Decimal:
        Assertion(value).must_be(int, float, Decimal)
        Assertion(percentage).must_be(str, int, float, Decimal, Percentage)

        percentage_value, _ = parse_percentage(percentage, 'percentage')
        return Decimal(value) * (1 + (percentage_value / Decimal(100)))

    @staticmethod
    def apply_percentage(value: Numeric, percentage: str | Numeric | Percentage) -> Decimal:
        Assertion(value).must_be(int, float, Decimal)
        Assertion(percentage).must_be(str, int, float, Decimal, Percentage)

        percentage_value, _ = parse_percentage(percentage, 'percentage')
        return Decimal(value) * (percentage_value / Decimal(100))

    @staticmethod
    def get_percentage(value1: Numeric, value2: Numeric) -> Percentage:
        Assertion(value1).must_be(int, float, Decimal)
        Assertion(value2).must_be(int, float, Decimal)

        if value2 == 0:
            raise ZeroDivisionError(f'Cannot calculate percentage with "value2" being zero')

        percentage_value: Decimal = (Decimal(value1) / Decimal(value2)) * 100
        return Percentage(percentage_value)

    def is_zero(self) -> bool:
        return self.__value == 0.0

    @property
    def value(self) -> Decimal:
        return self.__value

    @property
    def percentage(self) -> Decimal:
        return self.__value

    @property
    def fraction(self) -> Decimal:
        return self.__value / Decimal(100)
    
    @property
    def limits(self) -> tuple[Decimal, Decimal] | None:
        return self.__limits
