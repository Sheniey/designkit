
import importlib
from pathlib import Path
from typing import overload, TextIO, BinaryIO, Literal
from abc import ABC, abstractmethod
from types import ModuleType

from designkit.creational.backend.exceptions import CodecDependencyUnavailable


MSGSPEC_ENCODING_ORDER = Literal['deterministic', 'sorted']


class CodecProtocol(ABC):
    mod: ModuleType
    """The codec module that implements the actual encoding and decoding logic."""

    # data.json/<buf:data.json> -> decode() -> object
    @staticmethod
    @overload
    @abstractmethod
    def load[T](path: Path, *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @staticmethod
    @overload
    @abstractmethod
    def load[T](buffer: TextIO | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @staticmethod
    @abstractmethod
    def load[T](path_or_buffer: Path | TextIO | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T:
        pass


    # object -> encode() -> data.json/<buf:data.json>
    @staticmethod
    @overload
    @abstractmethod
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @staticmethod
    @overload
    @abstractmethod
    def save[T](data: T, buffer: TextIO | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @staticmethod
    @abstractmethod
    def save[T](data: T, path_or_buffer: Path | TextIO | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        pass


    # str -> object
    @staticmethod
    @abstractmethod
    def parse[T](data: str | bytes, schema: type, *args, **kwargs) -> T:
        pass


def check_codec_dependency(mod_name: str, codec_name: str) -> ModuleType:
    try:
        return importlib.import_module(mod_name)
    except ImportError:
        raise CodecDependencyUnavailable(codec_name, mod_name)


def read_text(path_or_buffer: Path | TextIO | BinaryIO, encoding: str = 'utf-8') -> str:
    """
    `encoding` used for reading text from the specified path.
    """
    if isinstance(path_or_buffer, Path):
        return path_or_buffer.read_text(encoding=encoding)
    if isinstance(path_or_buffer, TextIO | BinaryIO):
        return path_or_buffer.read()

def write_text(path_or_buffer: Path | TextIO | BinaryIO, data: str | bytes, encoding: str = 'utf-8') -> None:
    """
    `encoding` used for writing text to the specified path and decode `data` (bytes) to str.
    """
    if isinstance(data, bytes):
        data = data.decode(encoding)

    if isinstance(path_or_buffer, Path):
        path_or_buffer.write_text(data, encoding=encoding)
    if isinstance(path_or_buffer, TextIO | BinaryIO):
        path_or_buffer.write(data)


def read_bytes(path_or_buffer: Path | TextIO | BinaryIO, encoding: str = 'utf-8') -> bytes:
    """
    `encoding` used for reading bytes from the file <text> buffer.
    """
    if isinstance(path_or_buffer, Path):
        return path_or_buffer.read_bytes()
    if isinstance(path_or_buffer, TextIO):
        return path_or_buffer.read().encode(encoding)
    if isinstance(path_or_buffer, BinaryIO):
        return path_or_buffer.read()

def write_bytes(path_or_buffer: Path | TextIO | BinaryIO, data: str | bytes, encoding: str = 'utf-8') -> None:
    """
    `encoding` used for encode the `data` (str) to bytes.
    """
    if isinstance(data, str):
        data = data.encode(encoding)

    if isinstance(path_or_buffer, Path):
        path_or_buffer.write_bytes(data)
    if isinstance(path_or_buffer, TextIO | BinaryIO):
        path_or_buffer.write(data)
