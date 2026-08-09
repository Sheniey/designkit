
from functools import partial
from typing import Any
from designkit.behavioral.cache import cached
from decimal import Decimal
from abc import ABC, abstractmethod

type Numeric = int | float | Decimal
type Default = None

class DType[T, V](ABC):
    @abstractmethod
    def __init__(self, value: V) -> None: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @staticmethod
    @abstractmethod
    def validate(value: V) -> bool: ...

    @classmethod
    @abstractmethod
    def parse(self, value: V) -> T | None: ...

    @classmethod
    @abstractmethod
    def findall(self, text: str) -> list[T]: ...

    @property
    @abstractmethod
    def value(self) -> Any: ...

parser_cache = partial(cached, capacity=128)
"""Represents a `partial(cached, capacity=128)` function."""
