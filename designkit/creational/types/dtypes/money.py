
import re
from decimal import Decimal
from designkit.behavioral.cache import LRUCache
from typing import Final as Const, Callable, Self
from designkit.creational.types.dtypes.currency import (
    Currency, Currencies,
    MoneySpecifierFormat, DEFAULT_SPECIFIER
)
from designkit.creational.types.dtypes.percentage import Percentage
from designkit.behavioral.typing import Assertion, classname

from designkit.creational.types.utils import Numeric, Default, DType, parser_cache


currency_symbols: str = r'(\$|€|¥|£|S/|₹|₽|₩|₺|₴|₦|₫|฿|₡|₲|₵|₭|₮|₱|₸|₾|₼|₿|₢|₥|₰|₯|₠|₣|R$)'

pattern: re.Pattern = re.compile(
r'''
   # +$212.50 USD
((?P<sign1>
    [+-]
)?
(?P<symbol1>
    (''' + currency_symbols + r'''\s?)
)?
(?P<amount1>
    (\d+(([,]|[']+)\d{3})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
(?P<code1>
    (\s?[A-Z]{3})
)?
)| # USD +212.50
((?P<code2>[A-Z]{3})
\s?
(?P<sign2>[+-])?
(?P<amount2>
    (\d+(([,]|[']+)\d{3})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)| # +US$ 212.50
((?P<sign3>[+-])?
(?P<affix3>[a-zA-Z]{2,4})
\s?
(?P<amount3>
    (\d+(([,]|[']+)\d{3})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)| # +212.50€ EUR
((?P<sign4>
    [+-]
)?
(?P<amount4>
    (\d+(([,]|[']+)\d{3})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
(?P<symbol4>
    (\s?''' + currency_symbols + r''')
)?
(?P<code4>
    (\s?[A-Z]{3})
)?
)
''', re.VERBOSE)


MATCHER_MATCH: Const[str] = 'match'
MATCHER_FULLMATCH: Const[str] = 'fullmatch'
MATCHER_SEARCH: Const[str] = 'search'


def verify_currency(local_currency: Currency, external_currency: Currency, father: str) -> None:
    if local_currency != external_currency:
        raise ValueError(
            f'{father} must be exactly currency "{local_currency}" or a subcurrency of it.'
            f' Or you can exchange the currency of the other Money instance to "{local_currency}" using the "exchange_to" method.'
        )

def get_true_currency(currency: Currency) -> Currency:
    if currency.is_subcurrency:
        return currency.father_currency
    return currency

@parser_cache(skip_when=lambda args, kwargs: bool(args) and isinstance(args[0], Money))
def parse_money(
        value: str | Numeric | Money,
        currency: Currency | None,
        father: str = '',
        *,
        matcher: str = MATCHER_SEARCH
    ) -> tuple[Decimal, Currency, type]:

    if not Assertion(currency).should_be(Currency, None):
        raise TypeError(f'{father}\'s currency must be a Currency instance or None (auto-research the currency), got {classname(currency)}')

    if father == '':
        father = classname(Money)

    match (value, currency is not None):
        case str(), True:
            currency_pattern: re.Pattern = currency.pattern
            match = currency_pattern.__getattribute__(matcher)(value)
            if not match:
                raise ValueError(
                    f'{father} must be a valid money string like '
                    f'"{currency.format_amount(Decimal("212.50"), "informal")}" or '
                    f'"{currency.format_amount(Decimal("212.50"), "formal")}", '
                    f'got "{value}"'
                )
            sign: str = match.group('sign1') or match.group('sign2') or match.group('sign3') or ''
            raw_amount: str = (
                sign + (
                    match.group('amount1') or
                    match.group('amount2') or
                    match.group('amount3')
                )
            )
            amount: Decimal = Decimal(raw_amount.replace(',', '').replace("'", ''))
            true_currency: Currency = get_true_currency(currency)
            return amount, true_currency, str

        case str(), False:
            match = pattern.__getattribute__(matcher)(value)

            if not match:
                raise ValueError(
                    f'{father} must be a valid money string like "$212.50" or "212.50 USD", got "{value}"'
                )
            
            sign: str = match.group('sign1') or match.group('sign2') or match.group('sign3') or match.group('sign4') or ''
            raw_amount: str = (
                sign + (
                    match.group('amount1') or
                    match.group('amount2') or
                    match.group('amount3') or
                    match.group('amount4')
                )
            )
            amount: Decimal = Decimal(raw_amount.replace(',', '').replace("'", ''))
            true_currency: Currency
            if curr := (match.group('code1') or match.group('code2') or match.group('code4')):
                true_currency = Currency.get_by_code(curr)
            elif curr := match.group('affix3'):
                true_currency = Currency.get_by_affix(curr)
            elif curr := (match.group('symbol1') or match.group('symbol4')):
                true_currency = Currency.get_by_symbol(curr, symbol_place='suffix' if match.group('symbol4') is not None else 'prefix')
            else:
                raise ValueError(
                    f'No scraping case for the {father}\'s currency was matched, got "{value}"'
                )
            if true_currency is None:
                raise ValueError(
                    f'The currency for {father} must be preloaded, one scraping case matched but the currency was not found, got "{value}"'
                )

            return amount, true_currency, str
        
        case int(), True:
            amount: Decimal = Decimal(value)
            true_currency: Currency
            true_currency: Currency = get_true_currency(currency)
            return amount, true_currency, int
        
        case float(), True:
            amount: Decimal = Decimal(str(value))
            true_currency: Currency
            true_currency: Currency = get_true_currency(currency)
            return amount, true_currency, float
        
        case Decimal(), True:
            amount: Decimal = value
            true_currency: Currency
            true_currency: Currency = get_true_currency(currency)
            return amount, true_currency, Decimal

        case (int() | float() | Decimal()), False:
            raise ValueError(
                f'{father} can be a int, float, or Decimal only if a currency is provided, got "{value}"'
            )
        
        case Money(), _:
            amount: Decimal = value.value
            true_currency: Currency = value.true_currency
            return amount, true_currency, Money

        case _:
            raise TypeError(f'{father} must be a str, int, float, or Decimal, got {classname(value)}')


class Money(DType):
    # We must to support those notations:
    #  $212,  $ 212,  US$ 212,  $212 USD,  $ 212 USD,  212 USD,  USD 212
    # -$212, -$ 212, -US$ 212, -$212 USD, -$ 212 USD, -212 USD, USD -212
    # +$212, +$ 212, +US$ 212, +$212 USD, +$ 212 USD, +212 USD, USD +212
    # Some currencies does not have prefix, they have suffix intead such as 212€.
    # Also float numbers as Decimal such as $212.50, -$0.99; and dot as separator is obligatory.

    _exchange_rates: LRUCache[Decimal] = LRUCache(48)

    def __init__(self, value: str | Numeric, currency: Currency = Currencies.USD, *, _skip_parser: bool = False) -> None:
        """
        You can skip the parser (`_skip_parser=True`) to improve performance if you are sure that the value is a `Decimal` and the currency is correct.
        
        This is useful to avoid *one double-parsing*, such as `.parse`, `.__add__`, etc. In those cases, the value is already a `Decimal` and the currency is already correct, so you cannot use it when an `int`, `float` or `str` is provided.
        """
        value_validator = Assertion(value)
        value_validator.must_be(str, int, float, Decimal)
        Assertion(currency).must_be(Currency)

        if not _skip_parser:
            possible_money: tuple[Decimal, Currency, type] = parse_money(value, currency, classname(self), matcher=MATCHER_FULLMATCH)
            self.__value: Decimal = possible_money[0]
            self.__currency: Currency = currency # can be for example: EUR_ESP, ideal to format the amount as 212.50€ EUR (Spanish Peseta)
            self.__true_currency: Currency = possible_money[1] # so, this point to: EUR, ideal to comprobe if the currency is the same as another Money instance
        elif value_validator.should_be(Decimal):
            self.__value: Decimal = value
            self.__currency: Currency = currency
            self.__true_currency: Currency = currency
        else:
            raise ValueError(f'If you want to skip the parser in {classname(self)} to improve performance, the value must be a Decimal, got {classname(value)}')
        self.__raw_value: str = value

    def __str__(self) -> str:
        return self.__currency.format_amount(self.__value, 'formal')

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__currency.format_amount(self.__value, "all")})'

    def __format__(self, format_spec: str | MoneySpecifierFormat = 'comma:formal') -> str:
        """Recommended to use the `.format` method for consistent formatting of Money instances."""
        return self.format(format_spec)

    def __int__(self) -> int:
        return int(self.__value)

    def __float__(self) -> float:
        return float(self.__value)

    def __add__(self, other: str | Numeric | Money) -> Money:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        return Money(self.__value + other_value, self.__currency, _skip_parser=True)

    def __radd__(self, other: str | Numeric | Money) -> Money:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(other))
        return Money(other_value + self.__value, other_currency, _skip_parser=True)

    def __iadd__(self, other: str | Numeric | Money) -> Self:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        self.__value += other_value
        return self

    def __sub__(self, other: str | Numeric | Money) -> Money:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        return Money(self.__value - other_value, self.__currency, _skip_parser=True)

    def __rsub__(self, other: str | Numeric | Money) -> Money:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(other))
        return Money(other_value - self.__value, other_currency, _skip_parser=True)

    def __isub__(self, other: str | Numeric | Money) -> Self:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        self.__value -= other_value
        return self

    def __eq__(self, other: str | Numeric | Money) -> bool:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        try:
            verify_currency(self.__true_currency, other_currency, classname(self))
        except ValueError:
            return False
        return self.__value == other_value

    def __ne__(self, other: str | Numeric | Money) -> bool:
        other_value, other_currency, _ = parse_money(other, self.__currency, classname(self))
        try:
            verify_currency(self.__true_currency, other_currency, classname(self))
        except ValueError:
            return True
        return self.__value != other_value

    def __hash__(self) -> int:
        return hash((self.__value, self.__true_currency.code))

    def __copy__(self) -> Money:
        return Money(self.__value, self.__currency, _skip_parser=True)

    @staticmethod
    @parser_cache()
    def validate(value: str | Numeric | Money, currency: Currency | None = None) -> bool:
        try:
            parse_money(value, currency, 'value', matcher=MATCHER_FULLMATCH)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    @parser_cache()
    def parse(cls, value: str | Numeric | Money, currency: Currency | None = None) -> Money | None:
        money, true_currency, _ = parse_money(value, currency, classname(cls), matcher=MATCHER_FULLMATCH)
        return Money(money, true_currency, _skip_parser=True)

    @classmethod
    def findall(cls, text: str) -> list[Money]:
        Assertion(text).must_be(str)

        result: list[Money] = []
        matches = pattern.finditer(text)
        for match in matches:
            result.append(cls.parse(match.group(0)))
        return result
    
    def decrement(self, amount: str | Numeric | Money) -> Self:
        other_value, other_currency, _ = parse_money(amount, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        self.__value -= other_value
        return self

    def increment(self, amount: str | Numeric | Money) -> Self:
        other_value, other_currency, _ = parse_money(amount, self.__currency, classname(self))
        verify_currency(self.__true_currency, other_currency, classname(self))
        self.__value += other_value
        return self

    def discount(self, percentage: str | Numeric | Percentage) -> Self:
        Assertion(percentage).must_be(str, int, float, Decimal, Percentage)
        self.__value = Percentage.apply_reduction(self.__value, percentage)
        return self

    def increase(self, percentage: str | Numeric | Percentage) -> Self:
        Assertion(percentage).must_be(str, int, float, Decimal, Percentage)
        self.__value = Percentage.apply_increase(self.__value, percentage)
        return self

    def exchange_to(self, currency: Currency, exchange_rate: Numeric | None = Default) -> Self:
        Assertion(currency).must_be(Currency)
        Assertion(exchange_rate).must_be(int, float, Decimal, None)

        try:
            verify_currency(self.__true_currency, currency, classname(self))
        except ValueError:
            raise ValueError(f'Cannot exchange {classname(self)} to the same currency "{currency}" or a subcurrency of it. Please provide a different currency to exchange to.')

        exchange_rate_provided: bool
        match exchange_rate:
            case int():
                exchange_rate_provided = True
                exchange_rate: Decimal = Decimal(exchange_rate)
            case float():
                exchange_rate_provided = True
                exchange_rate: Decimal = Decimal(str(exchange_rate))
            case Decimal():
                exchange_rate_provided = True
                pass
            case None: # search for the exchange rate in the cache
                exchange_rate_provided = False
                try:
                    exchange_rate: Decimal = Money._exchange_rates.get(self.__currency.code + '->' + currency.code)
                except KeyError:
                    raise ValueError(
                        f'Exchange rate for {self.__currency} to {currency} is not provided. '
                        f'Please provide an exchange rate.'
                    )
            case _:
                raise TypeError(f'Exchange rate must be a int, float, Decimal, or None, got {classname(exchange_rate)}')
        
        if exchange_rate_provided:
            Money._exchange_rates.put(self.__currency.code + '->' + currency.code, exchange_rate)
            Money._exchange_rates.put(currency.code + '->' + self.__currency.code, Decimal('1') / exchange_rate)
        self.__value: Decimal = self.__value * exchange_rate
        self.__currency: Currency = currency
        self.__true_currency: Currency = get_true_currency(currency)
        return self

    def verify_currency(self, other: Money) -> bool:
        try:
            verify_currency(self.__true_currency, other.true_currency, classname(self))
            return True
        except ValueError:
            return False

    def format(self,
            formatter:
                  Callable[[Decimal, Currency], str]
                | MoneySpecifierFormat
                | str | None = DEFAULT_SPECIFIER
        ) -> str:
        """
        Format the monetary value according to the specified formatter.

        ## Parameters:
        formatter : Callable | Specifier | None - The format specifier, custom formatting function or default formatter.

        ## Specifiers

        ==============================

        `all` -> $2,120.50 USD (US Dollar)

        `informal` -> $2,120.50

        `formal` -> $2,120.50 USD
        > default

        `short` -> US$ 2,120.50

        `no_sign` -> 2,120.50 USD

        `textual` -> 2,120.50 US Dollars

        `en_textual` -> 2,120.50 US Dollars
        > uses the english naming convention for the currency

        `none` -> 2,120.50


        ## Precision (separated by "-")

        ==============================

        `.4f-formal` -> $212.5000 USD

        `.2f-informal` -> $212.50


        ## Separators (separated by ":")

        ==============================

        `comma:short` -> US$ 2,125,000.00
        > default

        `dot:textual` -> 2.125,000.00 US Dollars

        `pretty:informal` -> $2'125,000.00

        `simple:no_sign` -> 2120.50 USD


        ## Sample

        `.1f-pretty:informal` -> $2'125,000.0
        """
        match formatter:
            # custom formatter function
            case _ if callable(formatter):
                return formatter(self.__value, self.__currency)
            # predefined format specifiers
            case str():
                precision_match: re.Match | None = re.fullmatch(r'\.(\d+)[fF]-(.+)', formatter)
                if precision_match:
                    precision: int = int(precision_match.group(1))
                    specifier: str = precision_match.group(2)
                    return self.__currency.format_amount(self.__value, specifier, precision)
                return self.__currency.format_amount(self.__value, formatter)
            # just money with comma separation
            case None:
                return self.__currency.format_amount(self.__value, DEFAULT_SPECIFIER)
            # for unknown formatters
            case _:
                raise ValueError(f'The provided formatter "{formatter}" is not a function, specifier, or default (None) formatter.')

    def copy(self) -> Money:
        return Money(self.__value, self.__currency, _skip_parser=True)

    def is_negative(self) -> bool:
        return self.__value < 0

    def is_zero(self) -> bool:
        return self.__value == 0

    def is_fractional(self) -> bool:
        return self.__value % 1 != 0

    @property
    def value(self) -> Decimal:
        return self.__value

    @property
    def money(self) -> Decimal:
        return self.__value

    @property
    def currency(self) -> Currency:
        """
        Returns the currency of the Money instance, which can be a subcurrency.
        Ideally, this property should be used to format the amount of the Money instance.

        For example, if the Money instance has a currency of EUR_ESP (Spanish Peseta), this property will return EUR_ESP.
        If you want to compare the currency of two Money instances, use the `true_currency` property instead.
        """

        return self.__currency

    @property
    def true_currency(self) -> Currency:
        """
        Returns the true currency of the Money instance, which is the main currency if the current currency is a subcurrency.
        Ideally, this property should be used to compare the currency of two Money instances.

        For example, if the Money instance has a currency of EUR_ESP (Spanish Peseta), this property will return EUR (Euro).
        """
        return self.__true_currency
