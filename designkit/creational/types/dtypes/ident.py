
import re
from dataclasses import dataclass
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Self, Never

from designkit.creational.types.utils import Numeric, DType, parser_cache, Default

pattern: re.Pattern = re.compile(
    r'\w[a-zA-Z0-9_]*',
    re.UNICODE
)

class Identifier(DType):
    def __init__(self, value: str, blacklist: list[str]) -> None:
        Assertion(value).must_be(str)
        Assertion(blacklist).must_be(list)

        Identifier.validate(value, blacklist)

        self.__value: str = value
        self.__blacklist: list[str] = blacklist

    def __str__(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value})'

    @staticmethod
    def validate(value: str, blacklist: list[str]) -> bool:
        Assertion(value).must_be(str)
        Assertion(blacklist).must_be(list)

        try:
            match = pattern.fullmatch(value)
            if match is None:
                return False
            
            ident: str = match.group(0)
            if ident in blacklist:
                return False
            
        except Exception:
            return False
        return True

    @classmethod
    def parse(cls, value: str, blacklist: list[str]) -> Identifier:
        Assertion(value).must_be(str)
        Assertion(blacklist).must_be(list)

        return cls(value, blacklist)

    @classmethod
    def findall(cls, text: str, blacklist: list[str]) -> list[Identifier]:
        Assertion(text).must_be(str)
        Assertion(blacklist).must_be(list)

        identifiers: list[Identifier] = []
        for match in pattern.finditer(text):
            ident: str = match.group(0)
            if ident not in blacklist:
                identifiers.append(cls(ident, blacklist))
        return identifiers

    @property
    def value(self) -> str:
        return self.__value

    @property
    def ident(self) -> str:
        return self.__value

    @property
    def blacklist(self) -> list[str]:
        return self.__blacklist

