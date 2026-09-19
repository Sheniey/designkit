
import re, httpx
from validators import ipv4 as validate_ipv4, ipv6 as validate_ipv6
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Literal

from designkit.creational.types.utils import DType, parser_cache

type IPv4Aliasses = Literal['localhost', 'broadcast', 'any']
type HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']


ipv4_pattern: re.Pattern = re.compile(
    r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
)
ipv4_with_aliasses_pattern: re.Pattern = re.compile(
    r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|localhost|broadcast|any)'
)
ipv6_pattern: re.Pattern = re.compile(r'([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}')

@parser_cache()
def parse_ipv4(value: str | int | IPv4, father: str) -> str:
    match value:
        case 'localhost'|'LOCALHOST':
            return '127.0.0.1'

        case 'broadcast'|'BROADCAST':
            return '255.255.255.255'

        case 'any'|'ANY':
            return '0.0.0.0'

        case str():
            match = ipv4_pattern.fullmatch(value.strip())
            if not match or not validate_ipv4(value):
                raise ValueError(f'{father} must be a valid IPv4 address like "127.0.0.1", got "{value}"')
            return value

        case int():
            if not (0 <= value <= 4294967295):
                raise ValueError(f'{father} must be a valid IPv4 address like "4294967295", got "{value}"')
            return str((value >> 24) & 0xFF) + '.' + str((value >> 16) & 0xFF) + '.' + str((value >> 8) & 0xFF) + '.' + str(value & 0xFF)

        case IPv4():
            return value.value

@parser_cache()
def parse_ipv6(value: str | IPv6, father: str) -> str:
    match value:
        case str():
            value = value.strip()
            if not validate_ipv6(value):
                raise ValueError(f'{father} must be a valid IPv6 address like "2001:0db8:85a3:0000:0000:8a2e:0370:7334", got "{value}"')
            return value

        case IPv6():
            return value.value

class IPv4(DType['IPv4', str | int | 'IPv4']):
    IP_ANY: str         = '0.0.0.0'
    IP_LOCALHOST: str   = '127.0.0.1'
    IP_BROADCAST: str   = '255.255.255.255'

    def __init__(self, value: str | int | IPv4Aliasses) -> None:
        possible_value: str = parse_ipv4(value, classname(self))
        self.__value: str = possible_value

    @staticmethod
    def validate(value: str | IPv4, mode: Literal['with_aliasses', 'without_aliasses'] = 'without_aliasses') -> bool:
        Assertion.must_be(value, str)

        pattern: re.Pattern
        match mode:
            case 'with_aliasses':
                pattern = ipv4_with_aliasses_pattern
            case 'without_aliasses':
                pattern = ipv4_pattern
            case _:
                raise ValueError(f'Unknown validation mode: {mode!r}')

        match = pattern.fullmatch(value.strip())
        if not match or not validate_ipv4(value):
            return False
        return True

    @classmethod
    def parse(cls, value: str | int | IPv4Aliasses, mode: Literal['with_aliasses', 'without_aliasses'] = 'without_aliasses') -> IPv4:
        Assertion.must_be(value, str, int)

        pattern: re.Pattern
        match mode:
            case 'with_aliasses':
                pattern = ipv4_with_aliasses_pattern
            case 'without_aliasses':
                pattern = ipv4_pattern
            case _:
                raise ValueError(f'Unknown validation mode: {mode!r}')

        match = pattern.fullmatch(str(value).strip())
        if not match or not validate_ipv4(str(value)):
            raise ValueError(f'{classname(cls)} must be a valid IPv4 address like "127.0.0.1", got "{value}"')
        return cls(value)

    def fetch(
            self,
            method: HTTPMethod,
            path: str = '/',
            data: Any | None = None,
            headers: dict[str, str] | None = None,
            *,
            scheme: Literal['http', 'https'] = 'http',
            timeout: float = 5.0,
            **kwargs
        ) -> httpx.Response:

        Assertion.must_be(method, str)
        Assertion.must_be(path, str)
        Assertion.must_be(data, dict, list, str, None)
        Assertion.must_be(headers, dict, None)
        Assertion.must_be(scheme, str)
        Assertion.must_be(timeout, (int, float))

        method = method.upper()
        if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT'):
            raise ValueError(f'Unknown HTTP method: {method!r}')

        url: str = f'{scheme}://{self.__value}{path}'
        with httpx.Client(timeout=timeout) as client:
            response: httpx.Response = client.request(method, url, data=data, headers=headers, **kwargs)
            return response

    async def fetch_async(
            self,
            method: HTTPMethod, path: str = '/',
            data: Any | None = None,
            headers: dict[str, str] | None = None,
            *,
            scheme: Literal['http', 'https'] = 'http', 
            timeout: float = 5.0,
            **kwargs
        ) -> httpx.Response:

        Assertion.must_be(method, str)
        Assertion.must_be(path, str)
        Assertion.must_be(data, dict, list, str, None)
        Assertion.must_be(headers, dict, None)
        Assertion.must_be(scheme, str)
        Assertion.must_be(timeout, int, float)

        method = method.upper()
        if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT'):
            raise ValueError(f'Unknown HTTP method: {method!r}')

        if scheme not in ('http', 'https'):
            raise ValueError(f'Unknown scheme: {scheme!r}')

        url: str = f'{scheme}://{self.__value}{path}'
        async with httpx.AsyncClient(timeout=timeout) as client:
            response: httpx.Response = await client.request(method, url, data=data, headers=headers, **kwargs)
            return response

    @property
    def value(self) -> str:
        return self.__value

    @property
    def address(self) -> str:
        return self.__value

class IPv6(DType['IPv6', str | 'IPv6']): ...
