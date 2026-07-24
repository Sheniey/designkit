
from abc import ABC, abstractmethod
from typing import Self


class AbstractHandler[Req, Res](ABC):
    @abstractmethod
    def set_next(self, handler: AbstractHandler[Req, Res]) -> AbstractHandler[Req, Res]:
        pass

    @abstractmethod
    def handle(self, request: Req) -> Res | None:
        pass

class Handler[Req, Res](AbstractHandler[Req, Res]):
    def __init__(self) -> None:
        self.__next_handler: Handler[Req, Res] | None = None

    def __repr__(self) -> str:
        fmt_next_handler: str = '' if self.__next_handler is None else f'>> {self.__next_handler!r}'
        return f'{self.__class__.__name__} {fmt_next_handler}'

    def set_next(self, handler: Handler[Req, Res]) -> Handler[Req, Res]:
        self.__next_handler = handler
        return handler

    def handle(self, request: Req) -> Res | None:
        if self.__next_handler:
            return self.__next_handler.handle(request)
        return None

class HandlerChain[Req, Res](AbstractHandler[Req, Res]):
    def __init__(self, *, handlers: list[Handler[Req, Res]] | None = None) -> None:
        self.__handlers: list[Handler[Req, Res]] = handlers or []

    def __repr__(self) -> str:
        return ' >> '.join(handler.__class__.__name__ for handler in self.__handlers)

    def __add__(self, handler: Handler[Req, Res] | list[Handler[Req, Res]]) -> Self:
        if isinstance(handler, list):
            self.__handlers.extend(handler)
        else:
            self.__handlers.append(handler)
        return self

    def set_handlers(self, handlers: list[Handler[Req, Res]]) -> None:
        self.__handlers = handlers

    def set_next(self, handler: Handler[Req, Res]) -> Handler[Req, Res]:
        self.__handlers.append(handler)
        return handler
    
    def handle(self, request: Req) -> Res | None:
        print(__name__)
        for handler in self.__handlers:
            response: Res | None = handler.handle(request)
            if response is not None:
                return response
        return None
