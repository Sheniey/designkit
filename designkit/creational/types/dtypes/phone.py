
import re, phonenumbers
from dataclasses import dataclass
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Self

from designkit.creational.types.utils import Numeric, DType, parser_cache

@dataclass
class PhoneData:
    country_code: int
    number: str
    censored_number: str
    extension: str | None
    region_code: str | None

@parser_cache()
def parse_phone(value: str | int | Phone, include_country: bool, father: str) -> phonenumbers.PhoneNumber:
    match value:
        case str():
            value = value.strip()
            number: str = (
                '+'
                if include_country and not value.startswith('+')
                else ''
            ) + value
            if not (8 <= len(number) <= 15):
                raise ValueError(f'Phone number "{number}" is invalid must be between 8 and 15 digits long')
            
            return phonenumbers.parse(number)
        
        case int():
            number: str = ('+' if include_country else '') + str(value).strip()
            if not (8 <= len(number) <= 15):
                raise ValueError(f'Phone number "{number}" is invalid must be between 8 and 15 digits long')

            return phonenumbers.parse(number)

        case Phone():
            return value.raw_data
        
        case _:
            raise TypeError(f'{father} must be a str, int, or Phone but got {classname(value)}')

class Phone(DType):
    def __init__(self, value: str | int, include_country: bool = False) -> None:
        self._set_number(value, include_country)

    def _set_number(self, value: str | int, include_country: bool = False) -> None:
        possible_raw_data: phonenumbers.PhoneNumber = parse_phone(value, include_country, classname(self))

        self.__raw_data: phonenumbers.PhoneNumber = possible_raw_data
        self.__data: PhoneData = PhoneData(
            country_code=possible_raw_data.country_code,
            number=str(possible_raw_data.national_number),
            censored_number=str(possible_raw_data.national_number)[:3] + '****' + str(possible_raw_data.national_number)[-4:],
            extension=possible_raw_data.extension,
            region_code=phonenumbers.region_code_for_number(possible_raw_data),
        )
        self.__value: str = self.__data.number

    @property
    def value(self) -> str:
        return self.__value

    @property
    def number(self) -> str:
        return self.__value

    @property
    def censored_number(self) -> str:
        return self.__data.censored_number

    @property
    def country_code(self) -> int:
        return self.__data.country_code

    @property
    def data(self) -> PhoneData:
        return self.__data

    @property
    def raw_data(self) -> phonenumbers.PhoneNumber:
        return self.__value
