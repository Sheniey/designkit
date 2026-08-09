
from dataclasses import dataclass
import re
from validators import hostname as validate_hostname
from designkit.behavioral.typing import Assertion, classname
from typing import Any, Self

from designkit.creational.types.utils import Numeric, DType, parser_cache

pattern: re.Pattern = re.compile(
    # extended latin
    r"([\u0100-\u017F\u0180-\u024F\u00A0-\u00FF]"
    # dot-atom
    + r"|[\u0100-\u017F\u0180-\u024F\u00A0-\u00FF0-9a-z!#$%&'*+/=?^_`{}|~\-]+"
    + r"(\.[\u0100-\u017F\u0180-\u024F\u00A0-\u00FF0-9a-z!#$%&'*+/=?^_`{}|~\-]+)*"
    # quoted-string
    + r'|"('
    + r"[\u0100-\u017F\u0180-\u024F\u00A0-\u00FF\001-\010\013\014\016-\037"
    + r"!#-\[\]-\177]|\\[\011.]"
    + r')*")',

    re.IGNORECASE,
)

@dataclass
class EmailParts:
    local_part: str
    domain_part: str

def verify_email(value: str, father: str) -> None:
    if not Assertion(value).should_be(str):
        raise TypeError(f'{father} must be a str, got {classname(value)}')

    if not value or value.count('@') != 1:
        raise ValueError(f'{father} must be a valid email address, got "{value}"')
    
    local_part, domain_part = value.rsplit('@', 1)

    if len(local_part) > 64 or len(domain_part) > 253:
        raise ValueError(f'{father} must be a valid email address, got "{value}"')

    if domain_part.startswith('[') and domain_part.endswith(']'):
        domain_part = domain_part.lstrip('[').rstrip(']')

    valid: bool = bool(
        validate_hostname(domain_part)
        if re.match(pattern, local_part)
        else False
    )

    if not valid:
        raise ValueError(f'{father} must be a valid email address, got "{value}"')

def get_email(value: str | Email, father: str) -> str:
    match value:
        case Email():
            return value.value
        case str():
            return value
        case _:
            raise TypeError(f'{father} must be a str or Email, got {classname(value)}')

@parser_cache()
def parse_email(value: str | Email, father: str) -> EmailParts:
    if Assertion(value).should_be(Email):
        return value.parts
    Assertion(value).must_be(str)

    if not value or value.count('@') != 1:
        raise ValueError(f'{father} must be a valid email address, got "{value}"')
     
    local_part, domain_part = value.rsplit('@', 1)
    return EmailParts(local_part=local_part, domain_part=domain_part)

class Email(DType):
    def __init__(self, email: str) -> None:
        possible_parts: EmailParts = parse_email(email, classname(self))
        verify_email(email, classname(self))

        self.__value: str = email
        self.__parts: EmailParts = possible_parts

    def __format__(self, format_spec: str = 'full') -> str:
        match format_spec:
            case ''|'full':
                return self.__value
            case 'parts'|'repr':
                return f'username={self.__parts.local_part}, hostname={self.__parts.domain_part}'
            case 'local'|'local_part'|'username':
                return self.__parts.local_part
            case 'domain'|'domain_part'|'host'|'hostname':
                return self.__parts.domain_part
            case _:
                return f'{self.__value:{format_spec}}'

    def __str__(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value})'

    def __bool__(self) -> bool:
        return True

    def __eq__(self, other: str | Email) -> bool:
        email: str = get_email(other, 'email')
        return self.__value == email

    def __ne__(self, other: str | Email) -> bool:
        email: str = get_email(other, 'email')
        return self.__value != email

    def __hash__(self) -> int:
        return hash(self.__value)

    def __len__(self) -> int:
        return len(self.__value)

    def __contains__(self, item: str | Email) -> bool:
        email: str = get_email(item, 'email')
        return email in self.__value

    def __copy__(self) -> Self:
        return Email(self.__value)

    def __getitem__(self, item: str) -> str:
        match item:
            case 0|'username'|'local'|'local_part':
                return self.__parts.local_part
            case 1|'hostname'|'host'|'domain'|'domain_part':
                return self.__parts.domain_part
            case _:
                raise AttributeError(f'{classname(self)} has no item/section "{item}"')

    def __setitem__(self, item: str, value: Any) -> None:
        raise AttributeError(f'{classname(self)} is immutable and does not support item/section assignment')

    def __delitem__(self, item: str) -> None:
        raise AttributeError(f'{classname(self)} is immutable and does not support item/section deletion')

    @staticmethod
    def validate(value: str | Email) -> bool:
        try:
            email = get_email(value, 'value')
            verify_email(email, 'Email')
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    @parser_cache()
    def parse(cls, value: str | Email) -> Email | None:
        Assertion(value).must_be(str, Email)
        match = re.fullmatch(pattern, str(value).strip())
        print(match)
        if not match:
            return None
        return cls(match[0])

    @classmethod
    def findall(cls, text: str) -> list[Email] | None:
        Assertion(text).must_be(str)
        matches = re.findall(pattern, text)
        if not matches:
            return None
        return [cls(match[0]) for match in matches]

    def verify(self) -> None:
        return NotImplemented

    @property
    def value(self) -> str:
        return self.__value

    @property
    def email(self) -> str:
        return self.__value

    @property
    def parts(self) -> EmailParts:
        return self.__parts
