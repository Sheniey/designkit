
from enum import Enum
from dataclasses import dataclass, field


# ==================================================
# Types
# ==================================================

type HTTPStatus = int | Enum



# ==================================================
# Abstract HTTP Response
# ==================================================

class HTTPResponse[T]:
    @staticmethod
    def resolve(value: T, status: HTTPStatus) -> HTTPResult[T]:
        s: int
        if isinstance(status, Enum):
            s: int = int(status.value)
        else:
            s: int = int(status)

        match s:
            case s if 100 <= s < 200:
                return Info(value=value, status=s)
            case s if 200 <= s < 300:
                return Success(value=value, status=s)
            case s if 300 <= s < 400:
                return Redirect(value=value, status=s)
            case s if 400 <= s < 500:
                return ClientFailure(value=value, status=s)
            case s if 500 <= s < 600:
                return ServerFailure(value=value, status=s)
            case _:
                raise ValueError(f"Invalid HTTP status code: {s}")



# ==================================================
# HTTP Response Types
# ==================================================

@dataclass(frozen=True)
class Info[T](HTTPResponse[T]):
    value: T
    status: int = field(default=100)

    def __post_init__(self) -> None:
        if not (100 <= self.status < 200):
            raise ValueError("Status code for Info must be in the range [100, 199]")

@dataclass(frozen=True)
class Success[T](HTTPResponse[T]):
    value: T
    status: int = field(default=200)

    def __post_init__(self) -> None:
        if not (200 <= self.status < 300):
            raise ValueError("Status code for Success must be in the range [200, 299]")

@dataclass(frozen=True)
class Redirect[T](HTTPResponse[T]):
    value: T
    status: int = field(default=300)

    def __post_init__(self) -> None:
        if not (300 <= self.status < 400):
            raise ValueError("Status code for Redirect must be in the range [300, 399]")

@dataclass(frozen=True)
class ClientFailure[T](HTTPResponse[T]):
    value: T
    status: int = field(default=400)

    def __post_init__(self) -> None:
        if not (400 <= self.status < 500):
            raise ValueError("Status code for ClientFailure must be in the range [400, 499]")
    
@dataclass(frozen=True)
class ServerFailure[T](HTTPResponse[T]):
    value: T
    status: int = field(default=500)

    def __post_init__(self) -> None:
        if not (500 <= self.status < 600):
            raise ValueError("Status code for ServerFailure must be in the range [500, 599]")



# ==================================================
# Type Aliases
# ==================================================

type HTTPResult[T] = (
      Info[T]
    | Success[T]
    | Redirect[T]
    | ClientFailure[T]
    | ServerFailure[T]
)
