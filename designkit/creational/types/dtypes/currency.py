
import re
from decimal import Decimal
from typing import Literal

from designkit.behavioral.typing import Assertion, classname
from designkit.creational.types.utils import parser_cache


type MoneySpecifierFormat = Literal['all', 'informal', 'formal', 'short', 'no_sign', 'textual', 'en_textual', 'none']
DEFAULT_SPECIFIER = 'comma:formal'


class Currency:
    # We must to support those notations:
    #  $212,  $ 212,  US$ 212,  $212 USD,  $ 212 USD,  212 USD,  USD 212
    # -$212, -$ 212, -US$ 212, -$212 USD, -$ 212 USD, -212 USD, USD -212
    # +$212, +$ 212, +US$ 212, +$212 USD, +$ 212 USD, +212 USD, USD +212
    # Some currencies does not have prefix, they have suffix intead such as 212€.
    # Also float numbers as Decimal such as $212.50, -$0.99; and dot as separator is obligatory.

    _currencies: dict[str, Currency] = {}

    def __init__(
            self,
            *,
            code: str = 'USD',
            symbol: str = '$',
            name: str = 'US Dollar',
            default_ndigits: int = 2,
            affix: str | None = None,
            symbol_place: Literal['prefix', 'suffix'] = 'prefix',
            is_subcurrency_of: Currency | None = None,
            local_name: tuple[str, str] | None = None,
            english_name: tuple[str, str] | None = None,
        ) -> None:

        Assertion(code).must_be(str)
        Assertion(symbol).must_be(str)
        Assertion(name).must_be(str)
        Assertion(default_ndigits).must_be(int)
        Assertion(affix).must_be(str, None)
        Assertion(symbol_place).must_be(str)
        Assertion(is_subcurrency_of).must_be(Currency, None)
        Assertion(local_name).must_be(tuple, None)
        Assertion(english_name).must_be(tuple, None)

        if affix is None:
            affix = code[:2] + symbol

        if symbol_place not in ('prefix', 'suffix'):
            raise ValueError(f'Currency symbol_place must be either "prefix" or "suffix", got "{symbol_place}"')

        self.__code: str = code
        self.__symbol: str = symbol
        self.__name: str = name
        self.__english_name: tuple[str, str] | None = english_name
        self.__local_name: tuple[str, str] | None = local_name
        self.__ndigits: int = default_ndigits
        self.__affix: str = affix
        self.__symbol_place: Literal['prefix', 'suffix'] = symbol_place
        self.__is_subcurrency_of: Currency | None = is_subcurrency_of
        self.__pattern: re.Pattern
        if self.__symbol_place == 'prefix':
            self.__pattern = re.compile(
rf'''
   # +$212.50 USD
((?P<sign1>
    [+-]
)?
(?P<symbol1>
    ({re.escape(self.__symbol)}\s?)
)?
(?P<amount1>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
(?P<code1>
    (\s?{re.escape(self.__code)})
)?
)| # USD +212.50
((?P<code2>{re.escape(self.__code)})
\s?
(?P<sign2>[+-])?
(?P<amount2>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)| # +US$ 212.50
((?P<sign3>[+-])?
(?P<affix3>{re.escape(self.__affix)})
\s?
(?P<amount3>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)
'''.replace(' ', ''), re.VERBOSE)
        else:


            self.__pattern = re.compile(
rf'''
  # +212.50€ EUR
((?P<sign1>
    [+-]
)?
(?P<amount1>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)?
(?P<symbol1>
    (\s?({re.escape(self.__symbol)}))
)
(?P<code1>
    (\s?{re.escape(self.__code)})
)?
)| # EUR +212.50
((?P<code2>{re.escape(self.__code)})
\s?
(?P<sign2>[+-])?
(?P<amount2>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)| # +EU€ 212.50
((?P<sign3>[+-])?
(?P<affix3>{re.escape(self.__affix)})
\s?
(?P<amount3>
    (\d+(([,]|[']+)\d{{3}})*)(\.\d+)?
    (?:[eE]\^?[+-]?\d+)?
)
)
'''.replace(' ', ''), re.VERBOSE)

        Currency._currencies[code] = self

    def __str__(self) -> str:
        return f'{self.__name} ({self.__code})'

    def __repr__(self) -> str:
        return f'{classname(self)}(symbol={self.__symbol!r}, code={self.__code!r}, name={self.__name!r})'

    def format_amount(self,
            amount: Decimal,
            specifier: MoneySpecifierFormat | str = DEFAULT_SPECIFIER,
            ndigits: int | None = None
        ) -> str:
        """
        Format the monetary value according to the specified formatter.
        
        ## Parameters:
        amount : Decimal - The monetary value to be formatted.
        specifier : MoneySpecifierFormat - The format specifier for the monetary value.
        ndigits : int | None - The number of decimal places to include in the formatted amount. If None, the recomended number of decimal places of the self currency is used.
        
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

        
        ## Separators (separated by ":")
        
        ==============================
        
        `comma:short` -> US$ 2,125,000.00
        > default
        
        `dot:textual` -> 2.125,000.00 US Dollars
        
        `pretty:informal` -> $2'125,000.00
        
        `simple:no_sign` -> 2120.50 USD
        
        
        ## Sample
        
        `pretty:informal` -> $2'125,000.0
        """
        Assertion(amount).must_be(Decimal)
        Assertion(specifier).must_be(str)
        Assertion(ndigits).must_be(int, None)

        if ':' in specifier:
            separator, representation = specifier.split(':', 1)
        else:
            separator, representation = 'comma', specifier or 'formal'

        if separator not in ('comma', 'dot', 'pretty', 'simple'):
            raise ValueError(f'Unknown separator mode: {separator!r}')

        if ndigits is None:
            ndigits = self.__ndigits
        elif ndigits < 0:
            raise ValueError(f'ndigits must be greater than or equal to zero, got {ndigits}')

        sign: str = '-' if amount < 0 else ''
        amount: Decimal = abs(amount)
        formatted_amount: str = f'{amount:,.{ndigits}f}'
        match separator:
            case 'dot':
                formatted_amount = formatted_amount.replace(',', '.', 1)
            case 'pretty':
                formatted_amount = formatted_amount.replace(',', "'", 1)
            case 'simple':
                formatted_amount = formatted_amount.replace(',', '')

        match representation:
            case 'all':
                formatted_name: str = (
                    (
                        self.__local_name[0] if amount == 1 else self.__local_name[1]
                    ) if self.__local_name is not None else self.__name
                )
                return (
                    f'{sign}{self.__symbol}{formatted_amount} {self.__code} ({formatted_name})'
                    if self.__symbol_place == 'prefix' else
                    f'{sign}{formatted_amount}{self.__symbol} {self.__code} ({formatted_name})'
                )
            case 'informal':
                return (
                    f'{sign}{self.__symbol}{formatted_amount}'
                    if self.__symbol_place == 'prefix' else
                    f'{sign}{formatted_amount}{self.__symbol}'
                )
            case 'formal':
                return (
                    f'{sign}{self.__symbol}{formatted_amount} {self.__code}'
                    if self.__symbol_place == 'prefix' else
                    f'{sign}{formatted_amount}{self.__symbol} {self.__code}'
                )
            case 'short':
                return f'{sign}{self.__affix} {formatted_amount}'
            case 'no_sign':
                return f'{sign}{formatted_amount} {self.__code}'
            case 'textual':
                formatted_name: str = (
                    (
                        self.__local_name[0] if amount == 1 else self.__local_name[1]
                    ) if self.__local_name is not None else self.__name
                )
                return f'{sign}{formatted_amount} {formatted_name}'
            case 'en_textual':
                formatted_name: str = (
                    (
                        self.__english_name[0] if amount == 1 else self.__english_name[1]
                    ) if self.__english_name is not None else self.__name
                )
                return f'{sign}{formatted_amount} {formatted_name}'
            case 'none':
                return f'{sign}{formatted_amount}'
            case _:
                raise ValueError(f'Unknown format representation: {representation}')

    @classmethod
    def get_by_code(cls, code: str) -> Currency | None:
        return cls._currencies.get(code.strip())

    @classmethod
    @parser_cache()
    def get_by_symbol(cls, symbol: str, *, symbol_place: Literal['prefix', 'suffix'] = 'prefix') -> Currency | None:
        """This has a tendency to the most valuable currency, because some currencies share the same symbol... such as USD and MXN, which USD takes precedence."""
        symbol = symbol.strip()
        for currency in cls._currencies.values():
            match (currency.symbol, symbol):
                case ('$', '$'):
                    return cls._currencies.get('USD')
                case ('£', '£'):
                    return cls._currencies.get('GBP')
                case ('€', '€'):
                    curr = cls._currencies.get('EUR')
                    return Currency(
                        code=curr.code,
                        symbol=curr.symbol,
                        name=curr.name,
                        default_ndigits=curr.default_ndigits,
                        affix=curr.affix,
                        symbol_place=symbol_place,
                    )
                case ('¥', '¥'):
                    raise ValueError(
                        'The symbol "¥" is too ambiguous, '
                        'it can be either Japanese Yen (JPY) or Chinese Yuan (CNY) '
                        'and none of these is more "superior" than the other. '
                        'Please be more specific.'
                    )
            
            if currency.symbol == symbol:
                return currency
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Currency | None:
        for currency in cls._currencies.values():
            if currency.name == name.strip():
                return currency
        return None

    @classmethod
    def get_by_affix(cls, affix: str) -> Currency | None:
        for currency in cls._currencies.values():
            if currency.affix == affix.strip():
                return currency
        return None

    @classmethod
    def get_by_symbol_place(cls, symbol_place: Literal['prefix', 'suffix']) -> list[Currency]:
        return [currency for currency in cls._currencies.values() if currency.symbol_place == symbol_place]

    @classmethod
    def get_all_preloaded_currencies(cls) -> list[Currency]:
        return list(cls._currencies.values())

    def check_for_ambiguity(self) -> list[Currency]:
        """
        Returns a list of currencies that share the same symbol as this currency.
        """
        ambiguous_currencies: list[Currency] = []
        for currency in self._currencies.values():
            if currency is not self and currency.symbol == self.symbol:
                ambiguous_currencies.append(currency)
        return ambiguous_currencies

    @property
    def pattern(self) -> re.Pattern:
        """
        Returns a regex pattern that matches the currency format.
        """
        return self.__pattern

    @property
    def value(self) -> str:
        return self.__code
    
    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def name(self) -> str:
        return self.__name

    @property
    def english_name(self) -> str | None:
        return self.__english_name[0] if self.__english_name is not None else None

    @property
    def local_name(self) -> str | None:
        return self.__local_name[0] if self.__local_name is not None else None

    @property
    def code(self) -> str:
        return self.__code

    @property
    def affix(self) -> str:
        return self.__affix

    @property
    def default_ndigits(self) -> int:
        return self.__ndigits

    @property
    def symbol_place(self) -> Literal['prefix', 'suffix']:
        return self.__symbol_place

    @property
    def is_subcurrency(self) -> bool:
        return self.__is_subcurrency_of is not None

    @property
    def father_currency(self) -> Currency | None:
        return self.__is_subcurrency_of

class Currencies:
    # ================================================== #
    # AMERICAN CURRENCIES                                #
    # ================================================== #
    CAN: Currency = Currency(
        code='CAD',
        symbol='$',
        name='Canadian Dollar',
        default_ndigits=2,
        affix='CA$',
        symbol_place='prefix',
        local_name=('Canadian Dollar', 'Canadian Dollars'),
        english_name=('Canadian Dollar', 'Canadian Dollars'),
    )
    USD: Currency = Currency(
        code='USD',
        symbol='$',
        name='US Dollar',
        default_ndigits=2,
        affix='US$',
        symbol_place='prefix',
        local_name=('US Dollar', 'US Dollars'),
        english_name=('US Dollar', 'US Dollars'),
    )
    MXN: Currency = Currency(
        code='MXN',
        symbol='$',
        name='Peso Mexicano',
        default_ndigits=2,
        affix='MX$',
        symbol_place='prefix',
        local_name=('Peso Mexicano', 'Pesos Mexicanos'),
        english_name=('Mexican Peso', 'Mexican Pesos'),
    )
    COP: Currency = Currency(
        code='COP',
        symbol='$',
        name='Peso Colombiano',
        default_ndigits=2,
        affix='CO$',
        symbol_place='prefix', 
        local_name=('Peso Colombiano', 'Pesos Colombianos'),
        english_name=('Colombian Peso', 'Colombian Pesos'),
    )
    # hermanos venezolanos, cómo lidian con dos monedas...
    VEB: Currency = Currency(
        code='VEB',
        symbol='Bs.',
        name='Bolivar Venezolano',
        default_ndigits=6,
        affix='VE$',
        symbol_place='suffix',
        local_name=('Bolívar Venezolano', 'Bolívares Venezolanos'),
        english_name=('Venezuelan Bolívar', 'Venezuelan Bolívars'),
    )
    VEF: Currency = Currency(
        code='VEF',
        symbol='Bs.F.',
        name='Bolivar Fuerte',
        default_ndigits=2,
        affix='VE$',
        symbol_place='suffix',
        local_name=('Bolívar Fuerte', 'Bolívares Fuertes'),
        english_name=('Venezuelan Bolívar Fuerte', 'Venezuelan Bolívars Fuertes'),
    )
    PEN: Currency = Currency(
        code='PEN',
        symbol='S/',
        name='Sol Peruano',
        default_ndigits=2,
        affix='S/',
        symbol_place='prefix',
        local_name=('Sol Peruano', 'Soles Peruanos'),
        english_name=('Peruvian Sol', 'Peruvian Soles')
    )
    BRL: Currency = Currency(
        code='BRL',
        symbol='R$',
        name='Real Brasileiro',
        default_ndigits=2,
        affix='R$',
        symbol_place='prefix',
        local_name=('Real Brasileiro', 'Reais Brasileiros'),
        english_name=('Brazilian Real', 'Brazilian Reals')
    )
    ARS: Currency = Currency(
        code='ARS',
        symbol='$',
        name='Peso Argentino',
        default_ndigits=2,
        affix='AR$',
        symbol_place='prefix',
        local_name=('Peso Argentino', 'Pesos Argentinos'),
        english_name=('Argentine Peso', 'Argentine Pesos')
    )

    # ================================================== #
    # EUROPEAN CURRENCIES                                #
    # ================================================== #
    EUR: Currency = Currency(
        code='EUR',
        symbol='€',
        name='Euro',
        default_ndigits=2,
        affix='EU€',
        symbol_place='prefix', # Commonly, the Euro symbol is placed before the amount, e.g., €100.
        local_name=('Euro', 'Euros'),
        english_name=('Euro', 'Euros')
    )
    EUR_ENG: Currency = Currency(
        is_subcurrency_of=EUR,
        code='EUR',
        symbol='€',
        name='Euro -- England',
        default_ndigits=2,
        affix='EU€',
        symbol_place='prefix', # In England, the Euro symbol is placed before the amount, e.g., €100.
        local_name=('Euro -- England', 'Euros -- England'),
        english_name=('Euro -- England', 'Euros -- England'),
    )
    EUR_ESP: Currency = Currency(
        is_subcurrency_of=EUR,
        code='EUR',
        symbol='€',
        name='Euro -- España',
        default_ndigits=2,
        affix='EU€',
        symbol_place='suffix', # In Spain, the Euro symbol is placed after the amount, e.g., 100€.
        local_name=('Euro -- España', 'Euros -- España'),
        english_name=('Euro -- Spain', 'Euros -- Spain'),
    )
    GBP: Currency = Currency(
        code='GBP',
        symbol='£',
        name='Pound Sterling',
        default_ndigits=2,
        affix='GB£',
        symbol_place='suffix',
        local_name=('Pound Sterling', 'Pounds Sterling'),
        english_name=('Pound Sterling', 'Pounds Sterling'),
    )
    RUB: Currency = Currency(
        code='RUB',
        symbol='₽',
        name='Российский рубль',
        default_ndigits=2,
        affix='RUB₽',
        symbol_place='suffix',
        local_name=('Российский рубль', 'Российские рубли'),
        english_name=('Russian Ruble', 'Russian Rubles'),
    )

    # ================================================== #
    # ASIAN CURRENCIES                                   #
    # ================================================== #
    JPY: Currency = Currency(
        code='JPY',
        symbol='¥',
        name='日本円',
        default_ndigits=0,
        affix='JP¥',
        symbol_place='prefix',
        local_name=('日本円', '日本円'),
        english_name=('Japanese Yen', 'Japanese Yens'),
    )
    CNY: Currency = Currency(
        code='CNY',
        symbol='¥',
        name='人民币',
        default_ndigits=2,
        affix='CN¥',
        symbol_place='prefix',
        local_name=('人民币', '人民币'),
        english_name=('Chinese Yuan', 'Chinese Yuans'),
    )
    KRW: Currency = Currency(
        code='KRW',
        symbol='₩',
        name='대한민국 원',
        default_ndigits=0,
        affix='KR₩',
        symbol_place='prefix',
        local_name=('대한민국 원', '대한민국 원'),
        english_name=('South Korean Won', 'South Korean Wons'),
    )
    INR: Currency = Currency(
        code='INR',
        symbol='₹',
        name='भारतीय रुपया',
        default_ndigits=2,
        affix='IN₹',
        symbol_place='prefix',
        local_name=('भारतीय रुपया', 'भारतीय रुपये'),
        english_name=('Indian Rupee', 'Indian Rupees'),
    )

#??????????????????????????????????
