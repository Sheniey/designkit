
from typing import Any, Callable

from .commands import FunctionCommandBuilder
from .models import ProcessMetadata


def implement_metadata(func: Callable[..., None]) -> Callable[..., ProcessMetadata]:
    def wrapper(*args: Any, **kwargs: Any) -> ProcessMetadata:
        metadata = ProcessMetadata(success=False)
        try:
            result = func(*args, **kwargs)
            metadata.success = True
            metadata.result = result
        except Exception as e:
            metadata.exception = e
        return metadata
    return wrapper

def function_as_command[F: Callable](func: F, *args: Any, **kwargs: Any) -> FunctionCommandBuilder[F]:
    return FunctionCommandBuilder[F](func, *args, **kwargs)

