
from typing import Any

from .http import (
    HTTPResult, HTTPResponse, Success, ClientFailure, ServerFailure
)

def my_fn(request: Any) -> HTTPResult[dict[str, Any]]:
    # do an API call, return an HTTPResponse with the result    
    return HTTPResponse.resolve({"message": "Hello, World!"}, 200)

result: HTTPResult[dict[str, Any]] = my_fn({})

match result:
    case Success(value=v):
        print(f"Success: {v}")
    case ClientFailure(value=v):
        print(f"Client Failure: {v}")
    case ServerFailure(value=v):
        print(f"Server Failure: {v}")
    case _:
        print("Unexpected status code")