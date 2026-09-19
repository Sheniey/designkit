
from decimal import Decimal
from datetime import date
from dataclasses import dataclass
from typing import overload

from designkit.creational.toolbox.utils import APICaller, APIProvider, MappingAdapter, ListAdapter


API_KEY: str | None = None

def login(api_key: str) -> None:
    global API_KEY
    API_KEY = api_key


