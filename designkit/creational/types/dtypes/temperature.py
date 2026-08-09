
import re
from dataclasses import dataclass
from decimal import Decimal
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Self, Never

from designkit.creational.types.utils import Numeric, DType, parser_cache, Default

celsius_pattern: re.Pattern = re.compile(r'([+-]?\d+(\.\d+)?)\s*(°C|C|celsius|Celsius)', re.IGNORECASE)
fahrenheit_pattern: re.Pattern = re.compile(r'([+-]?\d+(\.\d+)?)\s*(°F|F|fahrenheit|Fahrenheit)', re.IGNORECASE)
kelvin_pattern: re.Pattern = re.compile(r'([+-]?\d+(\.\d+)?)\s*(K|kelvin|Kelvin)', re.IGNORECASE)

def parse_temperature(value: str | Numeric | _TemperatureUnit, father: str) -> tuple[Decimal, _TemperatureUnit | None]:
    match value:
        case str():
            if celsius_match := celsius_pattern.fullmatch(value):
                return Decimal(celsius_match.group(1)), Celsius
            elif fahrenheit_match := fahrenheit_pattern.fullmatch(value):
                return Decimal(fahrenheit_match.group(1)), Fahrenheit
            elif kelvin_match := kelvin_pattern.fullmatch(value):
                return Decimal(kelvin_match.group(1)), Kelvin
            else:
                raise ValueError(f'{father} must be a valid temperature string, got "{value}"')
        case int():
            return Decimal(value), None
        case float():
            return Decimal(str(value)), None
        case Decimal():
            return value, None
        case _TemperatureUnit():
            return value.value, type(value)
        case _:
            raise TypeError(f'{father} must be a str, int, float, Decimal, or TemperatureUnit but got {classname(value)}')

class _TemperatureUnit(DType):
    def __init__(self, value: Decimal, symbol: str) -> None:
        self.__value: Decimal = value
        self.__symbol: str = symbol

    def __str__(self) -> str:
        return f'{self.__value} {self.__symbol}'

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value} {self.__symbol})'

    def __call__(self, value: Decimal) -> Self:
        self.__value: Decimal = value
        return self

    @staticmethod
    def validate(value: str | Numeric | _TemperatureUnit) -> bool:
        raise NotImplementedError("Subclasses must implement the parse method.")

    @classmethod
    def parse(cls, value: str | Numeric | _TemperatureUnit) -> _TemperatureUnit | None:
        raise NotImplementedError("Subclasses must implement the parse method.")

    @classmethod
    def findall(cls, value: str | Numeric | _TemperatureUnit) -> list[_TemperatureUnit]:
        raise NotImplementedError("Subclasses must implement the findall method.")

    @property
    def value(self) -> Decimal:
        return self.__value

    @property
    def temperature(self) -> Decimal:
        return self.__value

    @property
    def symbol(self) -> str:
        return self.__symbol

class Celsius(_TemperatureUnit):
    def __init__(self, value: str | Decimal) -> None:
        super().__init__(value, '°C')

    @classmethod
    def parse(cls, value: str | Numeric | _TemperatureUnit) -> Celsius | None:
        match = celsius_pattern.fullmatch(str(value))
        if not match:
            return None
        return cls(Decimal(match.group(1)))

    @classmethod
    def from_fahrenheit(cls, fahrenheit: Fahrenheit) -> Celsius:
        celsius_value = (fahrenheit.value - Decimal('32')) * Decimal('5') / Decimal('9')
        return cls(celsius_value)

    def to_fahrenheit(self) -> Fahrenheit:
        fahrenheit_value = (self.value * Decimal('9') / Decimal('5')) + Decimal('32')
        return Fahrenheit(fahrenheit_value)

    @classmethod
    def from_kelvin(cls, kelvin: Kelvin) -> Celsius:
        celsius_value = kelvin.value - Decimal('273.15')
        return cls(celsius_value)

    def to_kelvin(self) -> Kelvin:
        kelvin_value = self.value + Decimal('273.15')
        return Kelvin(kelvin_value)

class Fahrenheit(_TemperatureUnit):
    def __init__(self, value: str | Decimal) -> None:
        super().__init__(value, '°F')

    @classmethod
    def parse(cls, value: str | Numeric | _TemperatureUnit) -> Fahrenheit | None:
        match = fahrenheit_pattern.fullmatch(str(value))
        if not match:
            return None
        return cls(Decimal(match.group(1)))

    @classmethod
    def from_celsius(cls, celsius: Celsius) -> Fahrenheit:
        fahrenheit_value = (celsius.value * Decimal('9') / Decimal('5')) + Decimal('32')
        return cls(fahrenheit_value)

    def to_celsius(self) -> Celsius:
        celsius_value = (self.value - Decimal('32')) * Decimal('5') / Decimal('9')
        return Celsius(celsius_value)

    @classmethod
    def from_kelvin(cls, kelvin: Kelvin) -> Fahrenheit:
        fahrenheit_value = (kelvin.value - Decimal('273.15')) * Decimal('9') / Decimal('5') + Decimal('32')
        return cls(fahrenheit_value)

    def to_kelvin(self) -> Kelvin:
        kelvin_value = (self.value - Decimal('32')) * Decimal('5') / Decimal('9') + Decimal('273.15')
        return Kelvin(kelvin_value)

class Kelvin(_TemperatureUnit):
    def __init__(self, value: str | Decimal) -> None:
        super().__init__(value, 'K')

    @classmethod
    def parse(cls, value: str | Numeric | _TemperatureUnit) -> Kelvin | None:
        match = kelvin_pattern.fullmatch(str(value))
        if not match:
            return None
        return cls(Decimal(match.group(1)))

    @classmethod
    def from_celsius(cls, celsius: Celsius) -> Kelvin:
        kelvin_value = celsius.value + Decimal('273.15')
        return cls(kelvin_value)

    def to_celsius(self) -> Celsius:
        celsius_value = self.value - Decimal('273.15')
        return Celsius(celsius_value)

    @classmethod
    def from_fahrenheit(cls, fahrenheit: Fahrenheit) -> Kelvin:
        kelvin_value = (fahrenheit.value - Decimal('32')) * Decimal('5') / Decimal('9') + Decimal('273.15')
        return cls(kelvin_value)
    
    def to_fahrenheit(self) -> Fahrenheit:
        fahrenheit_value = (self.value - Decimal('273.15')) * Decimal('9') / Decimal('5') + Decimal('32')
        return Fahrenheit(fahrenheit_value)
    
class Temperature(DType):
    def __init__(self, value: str | Numeric | _TemperatureUnit, unit: _TemperatureUnit | None = None) -> None:
        Assertion(value).must_be(str, int, float, Decimal, _TemperatureUnit)
        Assertion(unit).must_be(_TemperatureUnit, None)

        self.__value: Decimal
        self.__unit: _TemperatureUnit
        if unit is not None:
            possible_temp = parse_temperature(value, classname(self))
            self.__value = possible_temp[0]
            self.__unit = possible_temp[1] if possible_temp[1] is not None else unit
        else:
            self.__unit = value
            self.__value = value.value

    def __str__(self) -> str:
        return f'{self.__value} {self.__unit.symbol}'

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value} {classname(self.__unit)})'

    @staticmethod
    def validate(value: str | Numeric | _TemperatureUnit) -> bool:
        match value:
            case str():
                return bool(
                    celsius_pattern.fullmatch(value) or
                    fahrenheit_pattern.fullmatch(value) or
                    kelvin_pattern.fullmatch(value)
                )
            case int() | float() | Decimal():
                return True
            case _TemperatureUnit():
                return True
            case _:
                return False

    @classmethod
    def parse(cls, value: str | Numeric | _TemperatureUnit) -> Temperature | None:
        match value:
            case str():
                if celsius_match := celsius_pattern.fullmatch(value):
                    return cls(Celsius(Decimal(celsius_match.group(1))))
                elif fahrenheit_match := fahrenheit_pattern.fullmatch(value):
                    return cls(Fahrenheit(Decimal(fahrenheit_match.group(1))))
                elif kelvin_match := kelvin_pattern.fullmatch(value):
                    return cls(Kelvin(Decimal(kelvin_match.group(1))))
                else:
                    return None
            case int() | float() | Decimal():
                return cls(Celsius(Decimal(value)))
            case _TemperatureUnit():
                return cls(value)
            case _:
                raise TypeError(f'{classname(cls)} must be a str, int, float, Decimal, or TemperatureUnit but got {classname(value)}')
    
    @classmethod
    def findall(cls, value: str | Numeric | _TemperatureUnit) -> list[Temperature]:
        if isinstance(value, str):
            matches = []
            for match in celsius_pattern.finditer(value):
                matches.append(cls(Celsius(Decimal(match.group(1)))))
            for match in fahrenheit_pattern.finditer(value):
                matches.append(cls(Fahrenheit(Decimal(match.group(1)))))
            for match in kelvin_pattern.finditer(value):
                matches.append(cls(Kelvin(Decimal(match.group(1)))))
            return matches
        elif isinstance(value, (int, float, Decimal)):
            return [cls(Celsius(Decimal(value)))]
        elif isinstance(value, _TemperatureUnit):
            return [cls(value)]
        else:
            raise TypeError(f'{classname(cls)} must be a str, int, float, Decimal, or TemperatureUnit but got {classname(value)}')

    @property
    def value(self) -> Decimal:
        return self.__value

    @property
    def unit(self) -> _TemperatureUnit:
        return self.__unit
