
from abc import ABC, abstractmethod
from typing import Any


class Policy(ABC):
    __slots__ = ('___latest_data', 'violated_if')


    violated_if: str = 'A policy is violated. LOL   -- this is a default message, please override it in your policy class.'

    def __init__(self) -> None:
        # hidden attribute...
        self.___latest_data: tuple[list[Any], dict[str, Any]] | None = None

    def __call__(self, *args, **kwargs) -> None:
        self.___latest_data = (list(args), dict(kwargs))
        self.apply(*args, **kwargs)

    def __rlshift__(
            self,
            other: Any | tuple[list[Any], dict[str, Any]] | Policy
        ) -> None:

        match other:
            # 5 >> IntegerPolicy() >> NonZeroNumberPolicy()
            case Policy():
                if other.___latest_data is not None:
                    args, kwargs = other.___latest_data
                    self(*args, **kwargs)
            # (5, ...) >> NonZeroNumberPolicy()
            case (list() as args, dict() as kwargs):
                self(*args, **kwargs)
            # 5 >> NonZeroNumberPolicy()
            case _:
                self(other)

    @abstractmethod
    def apply(self, *args, **kwargs) -> None:
        pass

