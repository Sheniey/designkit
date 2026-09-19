
from decimal import Decimal
from datetime import date
from dataclasses import dataclass
from typing import overload

from designkit.creational.types import Currency, Money
from designkit.creational.toolbox.utils import APICaller, APIProvider, MappingAdapter


@dataclass(frozen=True, slots=True)
class Translation:
    text: str
    src_lang: str
    tgt_lang: str


DEEPL_TRANSLATOR_ADAPTER = MappingAdapter(
    model=Translation,
    mapping=MappingAdapter(
        model=Translation,
        mapping={
            'detected_source_language': 'src_lang',
            'text': 'text'
        }
    )
)


async def translate(text: str, src_lang: str, tgt_lang: str, *, api_key: str) -> Translation:
    response: Translation = await APICaller(
        model=Translation,
        provider=APIProvider(
            name='DeepL API Translator',
            url='https://api.deepl.com/v2/translate',
            params={
                'text': text,
                'source_lang': src_lang,
                'target_lang': tgt_lang
            },
            adapter=DEEPL_TRANSLATOR_ADAPTER,
            need_api_key=True,
            api_key=api_key
        )
    ).fetch()
    return DEEPL_TRANSLATOR_ADAPTER.adapt(response)
