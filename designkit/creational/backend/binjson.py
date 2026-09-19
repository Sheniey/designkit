
from pathlib import Path
from types import ModuleType
from typing import BinaryIO, overload as over

from designkit.creational.backend.utils import (
    CodecProtocol, MSGSPEC_ENCODING_ORDER,
    check_codec_dependency,
    read_bytes, write_bytes
)


static = staticmethod

class BinJSONPerformanceCodec(CodecProtocol):
    """
    Binary JSON codec optimized for performance using the `orjson` library.

    - DOES NOT perform a Scheme/Model validation.
    - PRIORITIZES performance over validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('orjson', 'BinJSONPerformanceCodec')

    @static
    @over
    def load[T](path: Path, *args, **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T: ...
    
    @static
    def load[T](path_or_buffer: Path | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: bytes = read_bytes(path_or_buffer, encoding=encoding)
        return BinJSONPerformanceCodec.mod.loads(data, *args, **kwargs)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        payload: bytes = BinJSONPerformanceCodec.mod.dumps(data, *args, **kwargs)
        write_bytes(path_or_buffer, payload, encoding=encoding)

    @static
    def parse[T](data: bytes, *args, **kwargs) -> T:
        return BinJSONPerformanceCodec.mod.loads(data, *args, **kwargs)



class BinJSONBalancedCodec(CodecProtocol):
    """
    Binary JSON codec optimized for balanced performance and validation using the `msgspec.json` library.

    - Performs Scheme/Model validation using the provided schema.
    - BALANCES performance and validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('msgspec.json', 'BinJSONBalancedCodec')

    @static
    @over
    def load[T](
        path: Path,
        schema: type[T],
        *args,
        strict: bool = True,
        encoding: str = 'utf-8',
        **kwargs
    ) -> T: ...
    
    @static
    @over
    def load[T](
        buffer: BinaryIO,
        schema: type[T],
        *args,
        strict: bool = True,
        **kwargs
    ) -> T: ...

    @static
    def load[T](
        path_or_buffer: Path | BinaryIO,
        schema: type[T],
        *args,
        strict: bool = True,
        encoding: str = 'utf-8',
        **kwargs
    ) -> T:
        data: bytes = read_bytes(path_or_buffer, encoding=encoding)
        return BinJSONBalancedCodec.mod.decode(data, type=schema, strict=strict, *args, **kwargs)

    @static
    @over
    def save[T](
        data: T,
        path: Path,
        schema: type[T],
        *args,
        strict: bool = True,
        order: MSGSPEC_ENCODING_ORDER | None = None,
        encoding: str = 'utf-8',
        **kwargs
    ) -> None: ...

    @static
    @over
    def save[T](
        data: T,
        buffer: BinaryIO,
        schema: type[T],
        *args,
        strict: bool = True,
        order: MSGSPEC_ENCODING_ORDER | None = None,
        encoding: str = 'utf-8',
        **kwargs
    ) -> None: ...

    @static
    def save[T](
        data: T,
        path_or_buffer: Path | BinaryIO,
        schema: type[T],
        *args,
        strict: bool = True,
        order: MSGSPEC_ENCODING_ORDER | None = None,
        encoding: str = 'utf-8',
        **kwargs
    ) -> None:
        payload: bytes = BinJSONBalancedCodec.mod.encode(data, type=schema, strict=strict, order=order, *args, **kwargs)
        write_bytes(path_or_buffer, payload, encoding=encoding)

    @static
    def parse[T](data: bytes, schema: type[T], *args, order: MSGSPEC_ENCODING_ORDER | None = None, **kwargs) -> T:
        return BinJSONBalancedCodec.mod.decode(data, type=schema, order=order, *args, **kwargs)

    @static
    def Schema() -> type:
        base_mod: ModuleType = check_codec_dependency('msgspec', 'BinJSONBalancedCodec.Schema')
        return base_mod.Struct



class BinJSONValidatorCodec(CodecProtocol):
    """
    Binary JSON codec optimized for validation using the `pydantic` library.

    - Performs a STRICT Scheme/Model validation using Pydantic models.
    - DOES NOT focus on performance; prioritizes validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('pydantic', 'BinJSONValidatorCodec')

    @static
    @over
    def load[T](path: Path, model: type[T], *args, **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: BinaryIO, model: type[T], *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @static
    def load[T](path_or_buffer: Path | BinaryIO, model: type[T], *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: bytes = read_bytes(path_or_buffer, encoding=encoding)
        return model.model_validate_json(data)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        if hasattr(data, 'model_dump_json'):
            write_bytes(
                path_or_buffer,
                data.model_dump_json(*args, **kwargs),
                encoding=encoding
            )
        else:
            raise TypeError('BinJSONValidatorCodec.save() expects a Pydantic model with a model_dump_json() method')

    @static
    def parse[T](data: bytes, *args, encoding: str = 'utf-8', **kwargs) -> T:
        encoding = encoding.replace('-', '').lower()
        if hasattr(data, 'model_dump_json'):
            return data.model_dump_json(*args, **kwargs)
        else:
            raise TypeError('BinJSONValidatorCodec.parse() expects a Pydantic model with a model_dump_json() method')

    @static
    def BaseModel() -> type: return BinJSONValidatorCodec.mod.BaseModel


    
class BinJSONSafeCodec(CodecProtocol):
    """
    Binary JSON codec optimized for safety using the stdlib `json` library.

    - DOES NOT perform Scheme/Model validation.
    - Ensures backward compatibility.
    - MAY be SLOWER compared to other binary JSON codecs.
    """
    mod: ModuleType = check_codec_dependency('json', 'BinJSONSafeCodec')

    @static
    @over
    def load[T](path: Path, *args, **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @static
    def load[T](path_or_buffer: Path | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: bytes = read_bytes(path_or_buffer, encoding=encoding)
        return BinJSONSafeCodec.mod.loads(data, *args, **kwargs)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | BinaryIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        encoded: bytes = BinJSONSafeCodec.mod.dumps(data, *args, **kwargs).encode(encoding)
        write_bytes(path_or_buffer, encoded, encoding=encoding)

    @static
    def parse[T](data: bytes, *args, **kwargs) -> T:
        return BinJSONSafeCodec.mod.loads(data, *args, **kwargs)
    