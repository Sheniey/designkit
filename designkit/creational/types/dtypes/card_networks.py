
import re
from designkit.behavioral.typing import Assertion, classname
from dataclasses import dataclass
from enum import StrEnum, Enum
from typing import ClassVar, Pattern

class MII(Enum):
    """
    Major Industry Identifier (MII) for card networks.
    """

    ISO_ASSIGNMENT = 0
    AIRLINES = 1
    AIRLINES_AND_FINANCIAL = 2
    TRAVEL_AND_ENTERTAINMENT = 3
    BANKING_AND_FINANCIAL = 4
    MERCHANDISING_AND_BANKING = 5
    TELECOMMUNICATIONS = 6
    NATIONAL_ASSIGNMENT = 7
    RESERVED_FOR_FUTURE_USE = 8
    UNIVERSAL_ASSIGNMENT = 9


@dataclass(frozen=True, slots=True)
class IINRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(
                f'Invalid IIN range: {self.start} > {self.end}'
            )

        start_length = len(str(self.start))
        end_length = len(str(self.end))

        if start_length != end_length:
            raise ValueError(
                'IIN range boundaries must have the same number of digits'
            )

    @property
    def length(self) -> int:
        return len(str(self.start))

    def contains(self, value: int) -> bool:
        return self.start <= value <= self.end

class _TrieNode:
    __slots__ = (
        'children',
        'network',
        'ranges',
    )

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.network: CardNetwork | None = None
        self.ranges: list[tuple[IINRange, CardNetwork]] = []

class IINTrie:
    __slots__ = ('_root',)

    MAX_IIN_LENGTH = 8

    def __init__(self) -> None:
        self._root: _TrieNode = _TrieNode()

    def insert(
            self,
            iin: int | str,
            network: CardNetwork,
        ) -> None:
        
        Assertion(iin).must_be(int, str)
        Assertion(network).must_be(CardNetwork)
        value: str = str(iin)

        if not value.isdigit():
            raise ValueError(f'Invalid IIN: {iin!r}')

        # if not 6 <= len(value) <= self.MAX_IIN_LENGTH:
        #     raise ValueError(
        #         f'IIN must contain 6-8 digits. got {iin!r}'
        #     )

        node = self._root

        for digit in value:
            node = node.children.setdefault(digit, _TrieNode())

        if node.network is not None and node.network is not network:
            raise ValueError(
                f'IIN {iin} is already registered by '
                f'{node.network.name}'
            )

        node.network = network

    def insert_range(
        self,
        start: int | str,
        end: int | str,
        network: CardNetwork,
    ) -> None:
        start_value = int(start)
        end_value = int(end)

        iin_range = IINRange(start_value, end_value)

        node = self._root

        # El rango se indexa por su longitud.
        #
        # Ej:
        #
        # 222100-272099
        #
        # queda asociado conceptualmente al nivel de 6 dígitos.
        #
        # No generamos 49.999 entradas.
        for _ in range(iin_range.length):
            # No podemos saber un único camino del Trie para un
            # rango arbitrario, así que lo almacenamos en el root.
            #
            # lookup() resolverá el rango por longitud.
            break

        self._root.ranges.append((iin_range, network))

    def lookup(self, card_number: str) -> tuple[CardNetwork, int] | None:
        """
        Looks up the card network using the IIN, so... this may return a network even if the card number is invalid.

        When it successfully finds a network, it returns a tuple of the network and the length of the IIN that matched. E.g. `lookup("4...") -> (Visa, 6)`
        """
        Assertion(card_number).must_be(str)

        if not card_number.isdigit():
            return None

        node: _TrieNode = self._root
        best_network: CardNetwork | None = None
        best_length: int = -1

        for index, digit in enumerate(
            card_number[:self.MAX_IIN_LENGTH],
            start=1,
        ):
            child = node.children.get(digit)

            if child is None:
                break

            node: _TrieNode = child

            if node.network is not None:
                best_network = node.network
                best_length: int = index


        for iin_range, network in self._root.ranges:
            length = iin_range.length

            if len(card_number) < length:
                continue

            prefix: int = int(card_number[:length])

            if iin_range.contains(prefix):
                if length > best_length:
                    best_network = network
                    best_length = length
                elif length == best_length:
                    if (
                        best_network is not None
                        and best_network is not network
                    ):
                        raise ValueError(
                            f'Ambiguous IIN {prefix}: '
                            f'{best_network.name} vs '
                            f'{network.name}'
                        )

        return (best_network, best_length) if best_network is not None else None

    def clear(self) -> None:
        self._root = _TrieNode()



class CardNetwork:
    _networks: ClassVar[dict[str, CardNetwork]] = {}
    _iin_trie: ClassVar[IINTrie] = IINTrie()

    def __init__(
            self,
            name: str,
            *,
            miis: tuple[MII, ...] = (),
            iins: tuple[int | str, ...] = (),
            iin_ranges: tuple[tuple[int | str, int | str], ...] = (),
            pattern: str | Pattern[str] | None = None,
            security_code_lengths: tuple[int, ...] = (3,),
            security_code_protocol: str | None = None,
        ) -> None:

        Assertion(name).must_be(str)
        Assertion(pattern).must_be(str, Pattern, None)
        Assertion(security_code_lengths).must_be(tuple)
        Assertion(iins).must_be(tuple)
        Assertion(iin_ranges).must_be(tuple)
        Assertion(miis).must_be(tuple)
        Assertion(security_code_lengths).must_be(tuple)
        Assertion(security_code_protocol).must_be(str, None)

        self.__name: str = name
        self.__pattern: re.Pattern | None = None
        if Assertion(pattern).should_be(str):
            self.__pattern = re.compile(pattern)
        else:
            self.__pattern = pattern

        self.__security_code_lengths: tuple[int, ...] = security_code_lengths
        if security_code_protocol is None:
            raise ValueError(
                f'Please provide a security code protocol, such as "CVV2" or "CVC2".'
            )
        self.__security_code_protocol: str = security_code_protocol

        self.__iins: tuple[IINRange, ...] = tuple(
            IINRange(int(iin), int(iin))
            for iin in iins
        )
        self.__miis: tuple[MII, ...] = miis
        self.__iin_ranges: tuple[IINRange, ...] = tuple(
            IINRange(int(start), int(end))
            for start, end in iin_ranges
        )

        # Internal flags initialization
        self.__last_iin_length_lookup_flag: int | None = None

        # Registry a new network by name and IINs/IIN ranges.
        self._networks[name.lower()] = self

        for iin in self.__iins:
            self._iin_trie.insert(iin.start, self)
        
        for iin_range in self.__iin_ranges:
            self._iin_trie.insert_range(
                iin_range.start,
                iin_range.end,
                self,
            )

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__name!r})'

    @classmethod
    def get(cls, name: str) -> CardNetwork | None:
        return cls._networks.get(name.lower())

    def get_by_mii(self, mii: MII) -> tuple[CardNetwork, ...]:
        return tuple(
            network
            for network in CardNetworks.__dict__.values()
            if isinstance(network, CardNetwork) and mii in network.miis
        )

    @classmethod
    def find(cls, card_number: str | int) -> CardNetwork | None:
        """
        Finds the network using the IIN.

        This supports IINs of 6-8 digits and performs
        longest-prefix matching.
        """

        Assertion(card_number).must_be(str, int)
        number: str = str(card_number).strip()

        if not number.isdigit():
            return None


        result = cls._iin_trie.lookup(number)
        if result is None:
            return None
        network, length_flag = result
        network.last_iin_length_lookup_flag = length_flag
        return network

    def validate_number(self, card_number: str) -> bool:
        Assertion(card_number).must_be(str)
        if self.__pattern is None:
            return True

        return self.__pattern.fullmatch(card_number) is not None

    def validate_mii(self, card_number: str) -> bool:
        Assertion(card_number).must_be(str)

        if not self.__miis:
            return True
        
        if not card_number.isdigit():
            return False

        if not self.__miis:
            return True

        mii_digit: int = int(card_number[0])
        mii: MII = MII(mii_digit)

        return mii in self.__miis

    def validate_security_code(self, security_code: str | int | None) -> bool:
        Assertion(security_code).must_be(str, int, None)

        if security_code is None:
            return True

        value: str = str(security_code).strip()

        return (
            value.isdigit()
            and len(value) in self.__security_code_lengths
        )

    @property
    def last_iin_length_lookup_flag(self) -> int | None:
        return self.__last_iin_length_lookup_flag

    @last_iin_length_lookup_flag.setter
    def last_iin_length_lookup_flag(self, value: int | None) -> None:
        Assertion(value).must_be(int, None)
        self.__last_iin_length_lookup_flag = value

    @property
    def value(self) -> str:
        return self.__name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def pattern(self) -> re.Pattern | None:
        return self.__pattern

    @property
    def security_code_lengths(self) -> tuple[int, ...]:
        return self.__security_code_lengths

    @property
    def security_code_protocol(self) -> str | None:
        return self.__security_code_protocol

    @property
    def miis(self) -> tuple[MII, ...]:
        return self.__miis

    @property
    def iins(self) -> tuple[IINRange, ...]:
        return self.__iins

    @property
    def iin_ranges(self) -> tuple[IINRange, ...]:
        return self.__iin_ranges



class CardNetworks:
    VISA: CardNetwork = CardNetwork(
        'Visa',
        miis=(MII.BANKING_AND_FINANCIAL,),
        iins=('4',),
        pattern=r'4\d{12}(?:\d{3})?(?:\d{3})?',
        security_code_lengths=(3,),
        security_code_protocol='CVV2',
    )
    MASTERCARD: CardNetwork = CardNetwork(
        'Mastercard',
        miis=(
            MII.AIRLINES_AND_FINANCIAL,
            MII.BANKING_AND_FINANCIAL,
            MII.MERCHANDISING_AND_BANKING
        ),
        iin_ranges=(
            (51, 55),
            (222100, 272099),
        ),
        pattern=r'(?:5[1-5]\d{14}|2(?:2[2-9]\d{3}|[3-6]\d{4})\d{10})',
        security_code_lengths=(3,),
        security_code_protocol='CVC2',
    )
    AMERICAN_EXPRESS: CardNetwork = CardNetwork(
        'American Express',
        miis=(
            MII.TRAVEL_AND_ENTERTAINMENT,
        ),
        iins=('34', '37'),
        pattern=r'3[47]\d{13}',
        security_code_lengths=(4,),
        security_code_protocol='CID',
    )
    DISCOVER: CardNetwork = CardNetwork(
        'Discover',
        miis=(
            MII.TELECOMMUNICATIONS,
        ),
        iins=(
            '601100',
            '644000',
            '645000',
            '646000',
            '647000',
            '648000',
            '649000',
        ),
        pattern=r'6(?:011|5\d{2})\d{12}',
        security_code_lengths=(3,),
        security_code_protocol='CID',
    )
