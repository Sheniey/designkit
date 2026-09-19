
from decimal import Decimal
from datetime import date
from dataclasses import dataclass
from typing import overload

from designkit.creational.types import Currency, Money
from designkit.creational.toolbox.utils import APICaller, APIProvider, MappingAdapter, ListAdapter


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    from_currency: Currency
    to_currency: Currency
    rate: Decimal
    date: date

FRANKFURTER_ADAPTER = ListAdapter[ExchangeRate](
    model=ExchangeRate,
    mapping={
        'base': 'from_currency',
        'quote': 'to_currency',
        'rate': 'rate',
        'date': 'date'
    }
)


async def get_exchange_rate(from_currency: Currency, to_currency: Currency) -> ExchangeRate:
    response: ExchangeRate = await APICaller[ExchangeRate](
        model=ExchangeRate,
        provider=APIProvider(
            name='Frankfurter API',
            url=f'https://api.frankfurter.dev/v2/rate/{from_currency.value}/{to_currency.value}',
            adapter=FRANKFURTER_ADAPTER,
        )
    ).fetch() # type: ignore
    return response

@overload
async def convert(amount: Money, to_currency: Currency) -> Money: ...

@overload
async def convert(amount: Decimal, from_currency: Currency, to_currency: Currency) -> Decimal: ...

async def convert(
    amount: Money | Decimal,
    from_currency_or_to_currency: Currency,
    to_currency: Currency | None = None
) -> Money | Decimal:
    if isinstance(amount, Money):
        target_currency: Currency = from_currency_or_to_currency
        exchange_rate: ExchangeRate = await get_exchange_rate(
            amount.currency,
            target_currency
        )
        return amount.exchange_to(
            target_currency,
            exchange_rate.rate
        )
 
    if to_currency is None:
        raise TypeError('to_currency is required when converting a Decimal')
    exchange_rate: ExchangeRate = await get_exchange_rate(
        from_currency_or_to_currency,
        to_currency
    )
    return amount * exchange_rate.rate


