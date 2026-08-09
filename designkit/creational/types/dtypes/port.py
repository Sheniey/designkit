
import re
from designkit.behavioral.typing import Assertion, classname
from typing import Literal, Self

from designkit.creational.types.utils import Numeric, DType, parser_cache

soft_pattern: re.Pattern = re.compile(r'[:]?([0-9]{1,5})')
explicit_pattern: re.Pattern = re.compile(r':([0-9]{1,5})')

def verify_port(value: int, allowed: tuple[int, int] | list[int]) -> None:
    match allowed:
        case tuple() as allowed:
            if len(allowed) != 2:
                raise ValueError(f'Allowed tuple must contain exactly two integers, got {allowed}')

            if any(not isinstance(port, int) or not (0 <= port <= 65535) for port in allowed):
                raise ValueError(f'Allowed tuple must contain only integers between 0 and 65535, got {allowed}')

            if not (allowed[0] <= value <= allowed[1]):
                raise ValueError(f'Port "{value}" is out of range ({allowed[0]}-{allowed[1]})')
        
        case list() as allowed:
            if any(not isinstance(port, int) or not (0 <= port <= 65535) for port in allowed):
                raise ValueError(f'Allowed list must contain only integers between 0 and 65535, got {allowed}')

            if value not in allowed:
                raise ValueError(f'Port "{value}" is not in the allowed list {allowed}')

@parser_cache()
def parse_port(value: str | int, father: str) -> int:
    match value:
        case int() as port:
            return port
        
        case str() as port_str:
            match: re.Match | None = soft_pattern.fullmatch(port_str)
            if match is None:
                raise ValueError(f'Port "{port_str}" is invalid')

            port: int = int(match.group(1))
            return port
        
        case _:
            raise TypeError(f'{father} must be an int or str, got {classname(value)}')



class Port(DType):
    RANGE_VALID: tuple[int, int] = (0, 1024)
    RANGE_REGISTERED: tuple[int, int] = (1025, 49151)
    RANGE_DYNAMIC: tuple[int, int] = (49152, 65535)
    RANGE_ANY: tuple[int, int] = (0, 65535)

    def __init__(self, value: int | str, *, allowed: tuple[int, int] | list[int] = RANGE_ANY) -> None:
        possible_port: int = parse_port(value, classname(self))
        verify_port(possible_port, allowed)

        self.__value: int = possible_port
        self.__allowed: tuple[int, int] | list[int] = allowed

    def __str__(self) -> str:
        return str(self.__value)

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value})'

    def __and__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(self.__value & other_value, allowed=self.__allowed)

    def __rand__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(other_value & self.__value, allowed=self.__allowed)

    def __iand__(self, other: str | int) -> Self:
        other_value: int = parse_port(other, 'other')
        new_value: int = self.__value & other_value
        verify_port(new_value, self.__allowed)
        self.__value = new_value
        return self

    def __or__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(self.__value | other_value, allowed=self.__allowed)

    def __ror__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(other_value | self.__value, allowed=self.__allowed)

    def __ior__(self, other: str | int) -> Self:
        other_value: int = parse_port(other, 'other')
        new_value: int = self.__value | other_value
        verify_port(new_value, self.__allowed)
        self.__value = new_value
        return self

    def __xor__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(self.__value ^ other_value, allowed=self.__allowed)

    def __rxor__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(other_value ^ self.__value, allowed=self.__allowed)

    def __ixor__(self, other: str | int) -> Self:
        other_value: int = parse_port(other, 'other')
        new_value: int = self.__value ^ other_value
        verify_port(new_value, self.__allowed)
        self.__value = new_value
        return self

    def __lshift__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(self.__value << other_value, allowed=self.__allowed)

    def __rlshift__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(other_value << self.__value, allowed=self.__allowed)

    def __ilshift__(self, other: str | int) -> Self:
        other_value: int = parse_port(other, 'other')
        new_value: int = self.__value << other_value
        verify_port(new_value, self.__allowed)
        self.__value = new_value
        return self

    def __rshift__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(self.__value >> other_value, allowed=self.__allowed)

    def __rrshift__(self, other: str | int) -> Port:
        other_value: int = parse_port(other, 'other')
        return Port(other_value >> self.__value, allowed=self.__allowed)

    def __irshift__(self, other: str | int) -> Self:
        other_value: int = parse_port(other, 'other')
        new_value: int = self.__value >> other_value
        verify_port(new_value, self.__allowed)
        self.__value = new_value
        return self

    def __bool__(self) -> bool:
        return self.__value != 0

    def __gt__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value > other_value

    def __ge__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value >= other_value

    def __lt__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value < other_value

    def __le__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value <= other_value

    def __eq__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value == other_value

    def __ne__(self, other: str | int) -> bool:
        other_value: int = parse_port(other, 'other')
        return self.__value != other_value

    @staticmethod
    def validate(value: int | str, *, allowed: tuple[int, int] | list[int] = RANGE_ANY) -> bool:
        Assertion.must_be(value, int, str)

        try:
            port: int = parse_port(value, 'Port')
            verify_port(port, allowed)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    @parser_cache()
    def parse(cls, value: int | str, mode: Literal['soft', 'explicit'] = 'soft', *, allowed: tuple[int, int] | list[int] = RANGE_ANY) -> Port | None:
        Assertion.must_be(value, int, str)

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
        return cls(match[0], allowed=allowed)

    @classmethod
    def findall(cls, text: str, mode: Literal['soft', 'explicit'] = 'soft', *, allowed: tuple[int, int] | list[int] = RANGE_ANY) -> list[Port]:
        Assertion.must_be(text, str)
        Assertion.must_be(allowed, tuple, list)

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
            return None
        return [cls(match[0], allowed=allowed) for match in matches]

    @property
    def value(self) -> int:
        return self.__value

    @property
    def port(self) -> int:
        return self.__value

    @property
    def allowed(self) -> tuple[int, int] | list[int]:
        return self.__allowed
