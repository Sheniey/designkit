
import re
from validators import url as validate_url
from dataclasses import dataclass

url_pattern: re.Pattern = re.compile(
    r"(?P<scheme>(?:http|ftp)s?://)"
    r"(?P<host>(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})"
    r"(?::(?P<port>\d+))?"
    r"(?P<path>/[^\s]*)?"
    r"(?P<query>\?[^\s]*)?"
    r"(?P<fragment>#\S*)?"
)

def parse_url(url: str | URL) -> ...:
    ...

class URL:
    def __init__(self, url: str) -> None:
        if not validate_url(url):
            raise ValueError(f'The provided URL "{url}" is invalid')
        
        self.url = url
        self.parsed = parse_url(url)

    @property
    def value(self) -> str:
        return self.url
