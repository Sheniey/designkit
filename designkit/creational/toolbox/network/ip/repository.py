
from dataclasses import dataclass

from designkit.creational.toolbox.utils import APICaller, APIProvider, MappingAdapter


@dataclass(frozen=True, slots=True)
class IPInfo:
    ip: str
    city: str
    region: str
    region_code: str
    country_code: str
    country_code_iso3: str
    country_name: str
    country_capital: str
    country_tld: str
    continent_code: str
    in_eu: bool
    postal: str
    latitude: float
    longitude: float
    timezone: str
    utc_offset: str
    country_calling_code: str
    currency: str
    currency_name: str
    languages: str
    asn: str
    org: str


IPAPI_ADAPTER = MappingAdapter[IPInfo](
    model=IPInfo,
    mapping={
        'ip': 'ip',
        'city': 'city',
        'region': 'region',
        'region_code': 'region_code',
        'country_code': 'country_code',
        'country_code_iso3': 'country_code_iso3',
        'country_name': 'country_name',
        'country_capital': 'country_capital',
        'country_tld': 'country_tld',
        'continent_code': 'continent_code',
        'in_eu': 'in_eu',
        'postal': 'postal',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'timezone': 'timezone',
        'utc_offset': 'utc_offset',
        'country_calling_code': 'country_calling_code',
        'currency': 'currency',
        'currency_name': 'currency_name',
        'languages': 'languages',
        'asn': 'asn',
        'org': 'org'
    }
)


async def extract(address: str) -> IPInfo:
    response: IPInfo = await APICaller[IPInfo](
        model=IPInfo,
        provider=APIProvider(
            name='ipapi',
            url=f'https://ipapi.co/{address}/json/',
            adapter=IPAPI_ADAPTER,
            retry=True,
        )
    ).fetch() # type: ignore
    return response
