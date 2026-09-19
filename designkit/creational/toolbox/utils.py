

import httpx
from typing import Any, Self, Protocol
from enum import Enum
from dataclasses import dataclass, field

from designkit.creational.types.dtypes.ip import HTTPMethod


class Adapter[T](Protocol[T]):
    def adapt(self, res: httpx.Response) -> T: ...

@dataclass
class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

@dataclass
class APIProvider[M]:
    url: str
    adapter: Adapter[M]
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    method: HTTPMethod = HTTPMethod.GET

    need_api_key: bool = False
    api_key: str | None = None
    name: str = '<unnamed>'
    timeout: float = 10.0
    retry: bool = False
    max_retries: int = 3

    def set_api_key(self, api_key: str) -> None:
        if not api_key:
            raise ValueError(f'API key is required for {self.name} but not provided.')
        self.api_key = api_key

class APICaller[M]:
    def __init__(self, model: M, provider: APIProvider[M]) -> None:
        self.__model: type[M] = model
        self.__providers: list[APIProvider[M]] = [provider]

    async def __call__(self) -> dict:
        return await self.run()

    def fallback(self, provider: APIProvider[M]) -> Self:
        self.__providers.append(provider)
        return self

    async def _fetch(self, provider: APIProvider[M]) -> M:
        try:
            async with httpx.AsyncClient() as client:
                if provider.need_api_key and not provider.api_key:
                    raise ValueError(f'API key is required for {provider.name} but not provided.')
                
                response = await client.request(
                    provider.method.value,
                    provider.url,
                    params=provider.params,
                    headers=provider.headers | ({'Authorization': f'Bearer {provider.api_key}'} if provider.api_key else {}),
                    timeout=provider.timeout,
                )
                response.raise_for_status()
                payload: M = provider.adapter.adapt(response)
                return self.__model(**payload)
        except httpx.RequestError as e:
            print(f'Request error for {provider.url}: {e}')
        except httpx.HTTPStatusError as e:
            print(f'HTTP error for {provider.url}: {e.response.status_code} - {e.response.text}')
    
    async def fetch(self) -> M:
        for provider in self.__providers:
            retries = 0
            while retries < (provider.max_retries if provider.retry else 1):
                try:
                    result = await self._fetch(provider)
                    if result is not None:
                        return result
                except Exception as e: ...
                retries += 1
        raise Exception('All API calls failed.')


class MappingAdapter[M]:
    """
    Adapter for handling JSON forms like this below:
    ```
    {
        "source_field": "value"
    }
    ```
    """
    def __init__(
        self,
        model: type[M],
        mapping: dict[str, str | MappingAdapter[M]]
    ) -> None:
        self.model: M = model
        self.mapping: dict[str, str | MappingAdapter[M]] = mapping

    def _resolve_value(self, source: str, value: Any, res: httpx.Response) -> Any:
        if isinstance(value, MappingAdapter):
            return value.adapt(httpx.Response(json={source: res.json().get(source)}), extras=None)
        return value

    def adapt(self, res: httpx.Response, extras: dict[str, Any] = None) -> M:
        values: dict[str, Any] = {
            target: self._resolve_value(source, target, res)
            for source, target in self.mapping.items()
        }
        if extras:
            values.update(extras)
        return self.model(**values)

class ListAdapter[M](MappingAdapter[M]):
    """
    Adapter for handling JSON forms like this below:
    ```
    [
        {
            "key1": "value1"
        },
        {
            "key2": "value2"
        }
    ]
    ```
    """
    def adapt(self, res: httpx.Response, extras: dict[str, Any] = None) -> list[M]:
        return [
            super().adapt(httpx.Response(json=item), extras=extras)
            for item in res.json()
        ]

class BlobAdapter:
    """
    Adapter for handling raw binary responses.
    """
    def adapt(self, res: httpx.Response, extras: dict[str, Any] = None) -> bytes:
        return res.content

