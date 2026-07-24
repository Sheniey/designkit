
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from .models import ProcessMetadata
from .exceptions import (
    UndoIsUndefinedError
)


class _Command:
    def __call__(self) -> None:
        self.execute()

    def __str__(self) -> str:
        return f'< {self.__class__.__name__} >'

    def __repr__(self) -> str:
        return str(self)



class Command(ABC, _Command):
    def __str__(self) -> str:
        return f'<[sync] {self.__class__.__name__} >'

    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...



class AsyncCommand(ABC, _Command):
    async def __call__(self) -> None:
        await self.execute()

    def __str__(self) -> str:
        return f'<[async] {self.__class__.__name__} >'

    @abstractmethod
    async def execute(self) -> None: ...

    @abstractmethod
    async def undo(self) -> None: ...



class ProcessCommand(ABC, _Command):
    def __str__(self) -> str:
        return f'<[multiprocess] {self.__class__.__name__} >'

    @abstractmethod
    def execute(self) -> ProcessMetadata: ...

    @abstractmethod
    def undo(self, metadata: ProcessMetadata) -> None: ...




class FunctionCommandBuilder[F: Callable[..., None]]:
    def __init__(self, execute_func: F) -> None:
        self._execute_fx: F = execute_func
        self._undo_fx: F | None = None

    def __call__(self, receiver) -> Command:
        execute_func: F = self._execute_fx
        undo_func: F | None = self._undo_fx

        class FunctionCommand(Command):
            def __init__(self, receiver: Any, *args: Any, **kwargs: Any) -> None:
                self.__receiver: Any = receiver
                self.__args: Any = args
                self.__kwargs: Any = kwargs

            def execute(self) -> None:
                return execute_func(self.__receiver, *self.__args, **self.__kwargs)

            def undo(self) -> None:
                if undo_func is None:
                    raise UndoIsUndefinedError(execute_func.__name__)
                return undo_func(self.__receiver, *self.__args, **self.__kwargs)

        return FunctionCommand(
            receiver,
            *self._execute_fx.__defaults__,   # args
            **self._execute_fx.__kwdefaults__ # kwargs
        )

    def undo(self, func: F) -> FunctionCommandBuilder[F]:
        self._undo_fx = func
        return self
