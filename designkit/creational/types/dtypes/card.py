
import re
from datetime import datetime
from designkit.behavioral.typing import Assertion, classname
from designkit.creational.types.dtypes.card_networks import MII, CardNetwork, CardNetworks

from designkit.creational.types.utils import DType, parser_cache


type MonthYear = tuple[int, int]

general_pattern: re.Pattern[str] = re.compile(
    r'(?P<number>\d{13,19})',
    re.UNICODE | re.VERBOSE,
)

expiration_pattern: re.Pattern = re.compile(
    r'(?P<month>0[1-9]|1[0-2])[-/](?P<year>\d{2}|\d{4})',
    re.UNICODE | re.VERBOSE
)

def validate_card(value: str | int, father: str) -> None:
    Assertion(value).must_be(str, int)
    if isinstance(value, int):
        value = str(value)

    number: str = value.strip()
    total: int = 0
    reverse: str = number[::-1]

    for i, digit in enumerate(reverse):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    if total % 10 != 0:
        raise ValueError(f'The Luhn Algorithm determined that {father} is an invalid card number. got "{value}"')

@parser_cache(skip_when=lambda value, code_length, code_protocol, father: isinstance(value, Card) or isinstance(value, int))
def parse_card(value: str | int | Card, code_length: int | None = None, code_protocol: str | int | None = None, father: str = '') -> tuple[str, CardNetwork]:
    Assertion(value).must_be(str, int, Card)

    if father == '':
        father = classname(Card)

    match value:
        case str():
            length: int = len(value)

            if length < 13:
                raise ValueError(f'{father} must be at least 13 characters long. got "{value}"')

            match: re.Match | None
            if 13 <= length <= 19:
                match = general_pattern.fullmatch(value)
            elif length > 19:
                match = general_pattern.search(value)

            if not match:
                raise ValueError(f'{father} must be a valid card number. got "{value}"')

            raw_number: str = match.group('number')
            validate_card(raw_number, father)
            network: CardNetwork | None = CardNetwork.find(raw_number)
            if network is None:
                raise ValueError(
                    f'No card network was found for {father}. '
                    f'got "{value}"'
                )

            if not network.validate_number(raw_number):
                raise ValueError(
                    f'The card network {network} rejected {father} '
                    f'because the card number does not match its pattern. '
                    f'got "{value}"'
                )
            number: str = match.group('number')
            return number, network
            
        case int():
            return parse_card(str(value), code_length, code_protocol, father)
        
        case Card():
            return value.value, value.network

        case _:
            raise ValueError(f'{father} must be a valid card number. got "{value}"')

@parser_cache(skip_when=lambda value, father: isinstance(value, Card) or isinstance(value, int))
def parse_expiration_date(value: str | int, father: str = '') -> tuple[int, int]:
    Assertion(value).must_be(str, int)

    if father == '':
        father = classname(Card)

    match value:
        case str():
            match: re.Match | None = expiration_pattern.fullmatch(value)
            if not match:
                raise ValueError(f'{father} must be a valid expiration date in the format MM/YY or MM/YYYY. got "{value}"')

            month: int = int(match.group('month'))
            year: int = int(match.group('year'))
            if year < 100:
                year += 2000

            return month, year

        case int():
            return parse_expiration_date(str(value), father)

        case _:
            raise ValueError(f'{father} must be a valid expiration date in the format MM/YY or MM/YYYY. got "{value}"')

class Card(DType):
    def __init__(self, value: str | int, expiration_date: str | int, security_code: str | int | None = None) -> None:
        Assertion(expiration_date).must_be(str, int)
        Assertion(security_code).must_be(str, int, None)

        self.__code: str | None = str(security_code).strip() if security_code is not None else None
        self.__code_length: int | None = len(self.__code) if self.__code else None
        number, network = parse_card(value, self.__code_length, None, classname(self))
        self.__number: str = number
        self.__network: CardNetwork = network
        self.__expiration_date: MonthYear = parse_expiration_date(expiration_date, classname(self))

    def _fmt_expiration_date(self) -> str:
        month, year = self.__expiration_date
        return f'{month:02d}/{year % 100:02d}'

    def __str__(self) -> str:
        return f'{self.__network}:{self.__number} ({self._fmt_expiration_date()})'

    def __repr__(self) -> str:
        return f'{self.__network}({self.__number})'

    @staticmethod
    @parser_cache()
    def validate(value: str | int, security_code: str | int | None = None) -> bool:
        try:
            code: str | None = str(security_code).strip() if security_code is not None else None
            code_length: int | None = len(code) if code else None
            parse_card(value, code_length, None, classname(Card))
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def parse(cls, value: str | int | Card, expiration_date: str | int | None = None, security_code: str | int | None = None) -> Card:
        Assertion(value).must_be(str, int, cls)
        if isinstance(value, cls):
            return value
        return cls(value, expiration_date, security_code)

    @classmethod
    def findall(cls, text: str) -> list[Card]:
        Assertion(text).must_be(str)
        result: list[Card] = []
        matches = general_pattern.finditer(text)
        for match in matches:
            result.append(cls(match.group(0)))
        return result

    def get_hidden_number(self, visible_digits: int = 4, char: str = '*') -> str:
        Assertion(visible_digits).must_be(int)
        Assertion(char).must_be(str)

        if visible_digits < 0:
            raise ValueError(f'visible_digits must be a non-negative integer. got "{visible_digits}"')

        hidden_part: str = self.__number[:-visible_digits]
        visible_part: str = self.__number[-visible_digits:]
        return hidden_part.replace(hidden_part, char * len(hidden_part)) + visible_part

    def is_expired(self) -> bool:
        current_year: int = datetime.now().year
        current_month: int = datetime.now().month
        exp_month, exp_year = self.__expiration_date
        return (exp_year < current_year) or (exp_year == current_year and exp_month < current_month)

    @property
    def last4(self) -> str:
        return self.__number[-4:]
    
    @property
    def value(self) -> str:
        return self.__number

    @property
    def number(self) -> str:
        return self.__number

    @property
    def mii(self) -> MII | None:
        """
        Returns the Major Industry Identifier (`MII`) of the card, which is the first digit of the card number. The `MII` indicates the category of the entity that issued the card.
        
        If the card network is not recognized or if the card network does not provide MII information, this property will return `None`.
        """
        return self.__network.miis

    @property
    def iin(self) -> str | None:
        """
        Returns the Issuer Identification Number (`IIN`) in current terms, also known as the Bank Identification Number (`BIN`).

        This property requires that the card number has been validated and that the card network has been identified. If the card network is not recognized or if the card number is invalid, this property will return `None` to avoid inventing a value.
        """
        iin_digits: int | None = self.__network.last_iin_length_lookup_flag
        if iin_digits is None:
            return None

        return self.__number[:iin_digits]
    
    @property
    def network(self) -> CardNetwork:
        return self.__network

    @property
    def expiry(self) -> MonthYear:
        return self.__expiration_date

    @property
    def security_code(self) -> str | int | None:
        return self.__code
