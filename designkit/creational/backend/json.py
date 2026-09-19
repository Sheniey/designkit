
from pathlib import Path
from types import ModuleType
from typing import TextIO, overload as over

from designkit.creational.backend.utils import (
    CodecProtocol, MSGSPEC_ENCODING_ORDER,
    check_codec_dependency,
    read_text, write_text
)


static = staticmethod

class JSONPerformanceCodec(CodecProtocol):
    """
    JSON codec optimized for performance using the `orjson` library.

    - DOES NOT perform a Scheme/Model validation.
    - PRIORITIZES performance over validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('orjson', 'JSONPerformanceCodec')

    @static
    @over
    def load[T](path: Path, *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: TextIO, *args, **kwargs) -> T: ...
    
    @static
    def load[T](path_or_buffer: Path | TextIO, *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: str = read_text(path_or_buffer, encoding=encoding)
        return JSONPerformanceCodec.mod.loads(data, *args, **kwargs)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        payload: bytes = JSONPerformanceCodec.mod.dumps(data, *args, **kwargs)
        write_text(path_or_buffer, payload, encoding=encoding)

    @static
    def parse[T](data: str, *args, **kwargs) -> T:
        return JSONPerformanceCodec.mod.loads(data, *args, **kwargs)

# import msgspec.json as msjson

# msjson.decode()

class JSONBalancedCodec(CodecProtocol):
    """
    JSON codec optimized for balanced performance and validation using the `msgspec.json` library.

    - Performs Scheme/Model validation using the provided schema.
    - BALANCES performance and validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('msgspec.json', 'JSONBalancedCodec')

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
        buffer: TextIO,
        schema: type[T],
        *args,
        strict: bool = True,
        **kwargs
    ) -> T: ...

    @static
    def load[T](
        path_or_buffer: Path | TextIO,
        schema: type[T],
        *args,
        strict: bool = True,
        encoding: str = 'utf-8',
        **kwargs
    ) -> T:
        data: str = read_text(path_or_buffer, encoding=encoding)
        return JSONBalancedCodec.mod.decode(data, type=schema, strict=strict, *args, **kwargs)

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
        buffer: TextIO,
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
        path_or_buffer: Path | TextIO,
        schema: type[T],
        *args,
        strict: bool = True,
        order: MSGSPEC_ENCODING_ORDER | None = None,
        encoding: str = 'utf-8',
        **kwargs
    ) -> None:
        payload: bytes = JSONBalancedCodec.mod.encode(data, type=schema, strict=strict, order=order, *args, **kwargs)
        write_text(path_or_buffer, payload, encoding=encoding)

    @static
    def parse[T](data: str, schema: type[T], *args, order: MSGSPEC_ENCODING_ORDER | None = None, **kwargs) -> T:
        return JSONBalancedCodec.mod.decode(data, type=schema, order=order, *args, **kwargs)

    @static
    def Schema() -> type:
        base_mod: ModuleType = check_codec_dependency('msgspec', 'JSONBalancedCodec.Schema')
        return base_mod.Struct



class JSONValidatorCodec(CodecProtocol):
    """
    JSON codec optimized for validation using the `pydantic` library.

    - Performs a STRICT Scheme/Model validation using Pydantic models.
    - DOES NOT focus on performance; prioritizes validation accuracy.
    """
    mod: ModuleType = check_codec_dependency('pydantic', 'JSONValidatorCodec')

    @static
    @over
    def load[T](path: Path, model: type[T], *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: TextIO, model: type[T], *args, **kwargs) -> T: ...

    @static
    def load[T](path_or_buffer: Path | TextIO, model: type[T], *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: str = read_text(path_or_buffer, encoding=encoding)
        return model.model_validate_json(data, *args, **kwargs)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        if hasattr(data, 'model_dump_json'):
            write_text(path_or_buffer, data.model_dump_json(*args, **kwargs), encoding=encoding)
        else:
            raise TypeError('JSONValidatorCodec.save() expects a Pydantic model with a model_dump_json() method')

    @static
    def parse[T](data: str, *args, encoding: str = 'utf-8', **kwargs) -> T:
        encoding = encoding.replace('-', '').lower()
        if hasattr(data, 'model_dump_json'):
            return data.model_dump_json(*args, encoding=encoding, **kwargs)
        else:
            raise TypeError('JSONValidatorCodec.save() expects a Pydantic model with a model_dump_json() method')

    @static
    def BaseModel() -> type: return JSONValidatorCodec.mod.BaseModel



class JSONSafeCodec(CodecProtocol):
    """
    JSON codec optimized for safety using the stdlib `json` library.

    - DOES NOT perform Scheme/Model validation.
    - Ensures backward compatibility.
    - MAY be SLOWER compared to other JSON codecs.
    """
    mod: ModuleType = check_codec_dependency('json', 'JSONSafeCodec')

    @static
    @over
    def load[T](path: Path, model: type[T], *args, encoding: str = 'utf-8', **kwargs) -> T: ...

    @static
    @over
    def load[T](buffer: TextIO, *args, **kwargs) -> T: ...

    @static
    def load[T](path_or_buffer: Path | TextIO, *args, encoding: str = 'utf-8', **kwargs) -> T:
        data: str = read_text(path_or_buffer, encoding=encoding)
        return JSONSafeCodec.mod.loads(data, *args, **kwargs)

    @static
    @over
    def save[T](data: T, path: Path, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    @over
    def save[T](data: T, buffer: TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None: ...

    @static
    def save[T](data: T, path_or_buffer: Path | TextIO, *args, encoding: str = 'utf-8', **kwargs) -> None:
        payload: bytes = JSONSafeCodec.mod.dumps(data, *args, **kwargs)
        write_text(path_or_buffer, payload, encoding=encoding)

    @static
    def parse[T](data: str, *args, **kwargs) -> T:
        return JSONSafeCodec.mod.loads(data, *args, **kwargs)
    