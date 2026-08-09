
import re, base64, binascii
from io import BufferedReader, BufferedWriter
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Self, Literal
from pathlib import Path

from designkit.creational.types.utils import Numeric, DType, parser_cache

pattern: re.Pattern = re.compile(r'[\x00-\xFF]+', re.UNICODE | re.VERBOSE)

class Blob(bytes, DType):
    def __new__(cls, value: Any | bytes | Blob) -> Self:
        if isinstance(value, Blob):
            value = bytes(value)
            return super().__new__(cls, value)
        
        try:
            value = bytes(value)
            return super().__new__(cls, value)
        except Exception as e:
            raise TypeError(f'{classname(cls)} must be bytes-like or Blob, got {classname(value)}') from e

    def __repr__(self) -> str:
        size: int = len(self)
        return f'{classname(self)}(0x{0:06X} ==> 0x{size:06X})'
    
    @staticmethod
    def validate(value: Any) -> bool:
        if isinstance(value, Blob):
            return True
        try:
            bytes(value)
            return True
        except Exception:
            return False

    @classmethod
    def parse(cls, value: str) -> Blob:
        Assertion(value).must_be(str)
        match = pattern.fullmatch(value)
        if not match:
            raise ValueError(f'{classname(cls)} must be a valid b-string like "\\x00", got "{value}"')
        return cls(value.encode('utf-8', errors='replace'))

    @classmethod
    def findall(cls, value: str) -> list[Blob]:
        Assertion(value).must_be(str)
        matches = pattern.findall(value)
        return [cls(match.encode('utf-8', errors='replace')) for match in matches]

    @classmethod
    def from_path(cls, path: Path) -> Blob:
        Assertion(path).must_be(Path)
        try:
            with open(path, 'rb') as f:
                return cls(f.read())
        except Exception as e:
            raise IOError(f'Failed to read file at path "{path}": {e}') from e

    def to_path(self, path: Path) -> None:
        Assertion(path).must_be(Path)
        try:
            with open(path, 'wb') as f:
                f.write(self)
        except Exception as e:
            raise IOError(f'Failed to write file at path "{path}": {e}') from e

    @classmethod
    def from_buffer(cls, file: BufferedReader) -> Blob:
        try:
            return cls(file.read())
        except Exception as e:
            raise IOError(f'Failed to read from file-like object: {e}') from e

    def to_buffer(self, file: BufferedWriter) -> None:
        try:
            file.write(self)
        except Exception as e:
            raise IOError(f'Failed to write to file-like object: {e}') from e

    @classmethod
    def from_hex(cls, hex_string: str) -> Blob:
        Assertion(hex_string).must_be(str)
        try:
            return cls(bytes.fromhex(hex_string))
        except ValueError as e:
            raise ValueError(f'Invalid hex string for {classname(cls)}: "{hex_string}"') from e

    def to_hex(self) -> str:
        return self.hex()

    @classmethod
    def from_base64(cls, b64_string: str) -> Blob:
        Assertion(b64_string).must_be(str)
        try:
            return cls(base64.b64decode(b64_string))
        except (ValueError, binascii.Error) as e:
            raise ValueError(f'Invalid base64 string for {classname(cls)}: "{b64_string}"') from e

    def to_base64(self) -> str:
        return base64.b64encode(self).decode('utf-8')

    @property
    def value(self) -> str:
        return self.decode('utf-8', errors='replace')

    @property
    def bytes(self) -> bytes:
        return bytes(self)
    