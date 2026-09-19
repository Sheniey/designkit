
import re, math
from collections.abc import Iterator
from decimal import Decimal
from typing import Literal, Self, overload

from designkit.behavioral.typing import Assertion, classname
from designkit.creational.types.utils import DType, Numeric, parser_cache


_LATITUDE_NUMBER: str = (
    r'[+-]?(?:90(?:\.0{1,6})?|(?:0|[1-8][0-9]?)(?:\.[0-9]{1,6})?)'
)
_LONGITUDE_NUMBER: str = (
    r'[+-]?(?:180(?:\.0{1,6})?|(?:0|[1-9][0-9]?|1[0-7][0-9])(?:\.[0-9]{1,6})?)'
)
_LATITUDE_AXIS: str = (
    rf'(?:(?P<latitude_direction_prefix>[NS])\s*)?'
    rf'(?P<latitude>{_LATITUDE_NUMBER})'
    rf'(?:\s*°)?'
    rf'(?:\s*(?P<latitude_direction_suffix>[NS]))?'
)
_LONGITUDE_AXIS: str = (
    rf'(?:(?P<longitude_direction_prefix>[EW])\s*)?'
    rf'(?P<longitude>{_LONGITUDE_NUMBER})'
    rf'(?:\s*°)?'
    rf'(?:\s*(?P<longitude_direction_suffix>[EW]))?'
)

latitude_pattern: re.Pattern[str] = re.compile(
    rf'(?<![\w.]){_LATITUDE_AXIS}(?![\w.])',
    re.ASCII | re.IGNORECASE | re.VERBOSE,
)
longitude_pattern: re.Pattern[str] = re.compile(
    rf'(?<![\w.]){_LONGITUDE_AXIS}(?![\w.])',
    re.ASCII | re.IGNORECASE | re.VERBOSE,
)
coordinate_pattern: re.Pattern[str] = re.compile(
    rf'(?<![\w.]){_LATITUDE_AXIS}\s*[,;]?\s*{_LONGITUDE_AXIS}(?![\w.])',
    re.ASCII | re.IGNORECASE | re.VERBOSE,
)
pattern: re.Pattern[str] = coordinate_pattern


def _numeric_to_float(value: Numeric, father: str) -> float:
    Assertion(value).must_be(int, float, Decimal)

    parsed: float = float(value)

    if not math.isfinite(parsed):
        raise ValueError(f'{father} must be finite, got {value!r}')
    return parsed

def _parse_axis_text(
    value: str,
    axis_pattern: re.Pattern[str],
    group_name: str,
    direction_group_name: str,
    positive_direction: str,
    negative_direction: str,
    father: str,
) -> float:
    stripped_value: str = value.strip()
    match: re.Match[str] | None = axis_pattern.fullmatch(stripped_value)
    if match is None:
        raise ValueError(
            f'{father} must be a valid {group_name} between '
            f'{'-90' if group_name == 'latitude' else '-180'} and '
            f'{'90' if group_name == 'latitude' else '180'} degrees, '
            f'with up to six decimal places, got {value!r}'
        )
    raw_value: str = match.group(group_name)
    prefix: str | None = match.group(f'{direction_group_name}_prefix')
    suffix: str | None = match.group(f'{direction_group_name}_suffix')
    return _apply_direction(
        raw_value,
        prefix,
        suffix,
        positive_direction,
        negative_direction,
        father,
    )


def _apply_direction(
    raw_value: str,
    prefix: str | None,
    suffix: str | None,
    positive_direction: str,
    negative_direction: str,
    father: str,
) -> float:
    if prefix is not None and suffix is not None:
        raise ValueError(
            f'{father} cannot contain both a prefix and suffix direction, '
            f'got {raw_value!r}'
        )

    numeric_value: float = float(raw_value)
    direction: str | None = (prefix or suffix)
    if direction is None:
        return numeric_value

    normalized_direction: str = direction.upper()
    explicit_sign: str = raw_value[0] if raw_value[0] in '+-' else ''
    if normalized_direction == positive_direction:
        if explicit_sign == '-':
            raise ValueError(
                f'{father} has a negative value incompatible with '
                f'direction {normalized_direction!r}'
            )
        return abs(numeric_value)

    if normalized_direction == negative_direction:
        if explicit_sign == '+':
            raise ValueError(
                f'{father} has a positive sign incompatible with '
                f'direction {normalized_direction!r}'
            )
        return -abs(numeric_value)

    raise ValueError(f'{father} has an invalid direction {direction!r}')

def _verify_range(value: float, minimum: float, maximum: float, father: str) -> None:
    if not minimum <= value <= maximum:
        raise ValueError(
            f'{father} must be between {minimum:g} and {maximum:g} degrees, '
            f'got {value:g}'
        )


@parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, Latitude))
def parse_latitude(
    value: str | Numeric | Latitude,
    father: str = 'Latitude',
) -> float:
    match value:
        case Latitude():
            parsed_value: float = value.value
        case str():
            parsed_value = _parse_axis_text(
                value,
                latitude_pattern,
                'latitude',
                'latitude_direction',
                'N',
                'S',
                father,
            )
        case int() | float() | Decimal():
            parsed_value = _numeric_to_float(value, father)
        case _:
            raise TypeError(f'{father} must be a str, int, float, Decimal, or Latitude; got {classname(value)}')

    _verify_range(parsed_value, -90.0, 90.0, father)
    return parsed_value

@parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, Longitude))
def parse_longitude(
    value: str | Numeric | Longitude,
    father: str = 'Longitude',
) -> float:
    match value:
        case Longitude():
            parsed_value: float = value.value
        case str():
            parsed_value = _parse_axis_text(
                value,
                longitude_pattern,
                'longitude',
                'longitude_direction',
                'E',
                'W',
                father,
            )
        case int() | float() | Decimal():
            parsed_value = _numeric_to_float(value, father)
        case _:
            raise TypeError(f'{father} must be a str, int, float, Decimal, or Longitude; got {classname(value)}')

    _verify_range(parsed_value, -180.0, 180.0, father)
    return parsed_value


@parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, (list, Coordinate)))
def parse_coordinate(
    value: str
    | tuple[str | Numeric | Latitude | Longitude, str | Numeric | Latitude | Longitude]
    | list[str | Numeric | Latitude | Longitude]
    | Coordinate,
    father: str = 'Coordinate',
) -> tuple[float, float]:
    match value:
        case Coordinate():
            return value.value
        case str():
            stripped_value: str = value.strip()
            match: re.Match[str] | None = coordinate_pattern.fullmatch(stripped_value)
            if match is None:
                raise ValueError(
                    f'{father} must be a valid coordinate in the format '
                    f'"40.7128 N, 74.0060 W" or "latitude, longitude", '
                    f'got {value!r}'
                )
            latitude: float = _apply_direction(
                match.group('latitude'),
                match.group('latitude_direction_prefix'),
                match.group('latitude_direction_suffix'),
                'N',
                'S',
                f'{father}.latitude',
            )
            longitude: float = _apply_direction(
                match.group('longitude'),
                match.group('longitude_direction_prefix'),
                match.group('longitude_direction_suffix'),
                'E',
                'W',
                f'{father}.longitude',
            )
            return latitude, longitude
        case tuple() | list():
            if len(value) != 2:
                raise ValueError(
                    f'{father} must contain exactly two values '
                    f'(latitude, longitude), got {len(value)}'
                )
            latitude = parse_latitude(value[0], f'{father}.latitude')
            longitude = parse_longitude(value[1], f'{father}.longitude')
            return latitude, longitude
        case _:
            raise TypeError(f'{father} must be a coordinate string, a pair of values, or Coordinate; got {classname(value)}')

def verify_coordinate(
    value: str
    | tuple[str | Numeric | Latitude | Longitude, str | Numeric | Latitude | Longitude]
    | list[str | Numeric | Latitude | Longitude]
    | Coordinate,
    father: str = 'Coordinate',
) -> None:
    parse_coordinate(value, father)

def _format_dms(value: float, hemisphere: str) -> str:
    absolute_value: float = abs(value)
    degrees: int = int(absolute_value)
    total_minutes: float = (absolute_value - degrees) * 60
    minutes: int = int(total_minutes)
    seconds: float = (total_minutes - minutes) * 60
    return f'{degrees}°{minutes:02d}\'{seconds:06.3f}" {hemisphere}'




class Latitude(DType):
    MIN_VALUE = -90.0
    MAX_VALUE = 90.0

    def __init__(self, value: str | Numeric | Latitude, *, _skip_parser: bool = False) -> None:
        self.__value: float = parse_latitude(value, classname(self)) if not _skip_parser else float(value)

    def __str__(self) -> str:
        return str(self.__value)

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value!r})'

    def __format__(self, format_spec: str = '') -> str:
        match format_spec:
            case 'dms':
                return _format_dms(self.__value, self.hemisphere)
            case 'direction':
                return f'{abs(self.__value):g}° {self.hemisphere}'
            case _:
                return format(self.__value, format_spec)

    def __float__(self) -> float:
        return self.__value

    def __int__(self) -> int:
        return int(self.__value)

    def __bool__(self) -> bool:
        return self.__value != 0.0

    def __hash__(self) -> int:
        return hash(self.__value)

    def _other_value(self, other: str | Numeric | Latitude) -> float:
        return parse_latitude(other, 'other')

    def __add__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self.__value + self._other_value(other))

    def __radd__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self._other_value(other) + self.__value)

    def __iadd__(self, other: str | Numeric | Latitude) -> Self:
        self.__value = parse_latitude(self.__value + self._other_value(other), classname(self))
        return self

    def __sub__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self.__value - self._other_value(other))

    def __rsub__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self._other_value(other) - self.__value)

    def __isub__(self, other: str | Numeric | Latitude) -> Self:
        self.__value = parse_latitude(self.__value - self._other_value(other), classname(self))
        return self

    def __mul__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self.__value * self._other_value(other))

    def __rmul__(self, other: str | Numeric | Latitude) -> Latitude:
        return type(self)(self._other_value(other) * self.__value)

    def __imul__(self, other: str | Numeric | Latitude) -> Self:
        self.__value = parse_latitude(self.__value * self._other_value(other), classname(self))
        return self

    def __truediv__(self, other: str | Numeric | Latitude) -> Latitude:
        other_value: float = self._other_value(other)
        if other_value == 0.0:
            raise ZeroDivisionError('Cannot divide a latitude by zero')
        return type(self)(self.__value / other_value)

    def __rtruediv__(self, other: str | Numeric | Latitude) -> Latitude:
        if self.__value == 0.0:
            raise ZeroDivisionError('Cannot divide by a latitude with value zero')
        return type(self)(self._other_value(other) / self.__value)

    def __itruediv__(self, other: str | Numeric | Latitude) -> Self:
        other_value: float = self._other_value(other)
        if other_value == 0.0:
            raise ZeroDivisionError('Cannot divide a latitude by zero')
        self.__value = parse_latitude(self.__value / other_value, classname(self))
        return self

    def __neg__(self) -> Latitude:
        return type(self)(-self.__value)

    def __pos__(self) -> Latitude:
        return type(self)(+self.__value)

    def __abs__(self) -> Latitude:
        return type(self)(abs(self.__value))

    def __round__(self, ndigits: int | None = None) -> Latitude:
        return type(self)(round(self.__value, ndigits))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Latitude):
            return self.__value == other.value
        if isinstance(other, (str, int, float, Decimal)) and not isinstance(other, bool):
            try:
                return self.__value == parse_latitude(other, 'other')
            except (TypeError, ValueError):
                return False
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: str | Numeric | Latitude) -> bool:
        return self.__value < self._other_value(other)

    def __le__(self, other: str | Numeric | Latitude) -> bool:
        return self.__value <= self._other_value(other)

    def __gt__(self, other: str | Numeric | Latitude) -> bool:
        return self.__value > self._other_value(other)

    def __ge__(self, other: str | Numeric | Latitude) -> bool:
        return self.__value >= self._other_value(other)

    def __copy__(self) -> Latitude:
        return type(self)(self.__value)

    def to_dms(self) -> tuple[int, int, float]:
        absolute_value: float = abs(self.__value)
        degrees: int = int(absolute_value)
        total_minutes: float = (absolute_value - degrees) * 60
        minutes: int = int(total_minutes)
        seconds: float = (total_minutes - minutes) * 60
        return degrees, minutes, seconds

    @staticmethod
    @parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, Latitude))
    def validate(value: str | Numeric | Latitude) -> bool:
        try:
            parse_latitude(value, 'Latitude')
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    @parser_cache(skip_when=lambda cls, value, *args, **kwargs: isinstance(value, Latitude))
    def parse(cls, value: str | Numeric | Latitude) -> Latitude | None:
        match value:
            case cls():
                return value
            case str():
                if latitude_pattern.fullmatch(value.strip()) is None:
                    return None
            case _:
                pass
        parsed_value: float = parse_latitude(value, classname(cls))
        return cls(parsed_value, _skip_parser=True)

    @classmethod
    def findall(cls, text: str) -> list[Latitude]:
        if not isinstance(text, str):
            raise TypeError(f'text must be a str, got {type(text).__name__}')
        return [cls(match.group('latitude')) for match in latitude_pattern.finditer(text)]

    @property
    def value(self) -> float:
        return self.__value

    @property
    def degrees(self) -> float:
        return self.__value

    @property
    def hemisphere(self) -> Literal['N', 'S']:
        return 'N' if self.__value >= 0.0 else 'S'


class Longitude(DType):
    MIN_VALUE = -180.0
    MAX_VALUE = 180.0

    def __init__(self, value: str | Numeric, *, _skip_parser: bool = False) -> None:
        Assertion(value).must_be(str, int, float, Decimal)

        self.__value: float = parse_longitude(value, classname(self)) if not _skip_parser else float(value)

    def __str__(self) -> str:
        return str(self.__value)

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__value!r})'

    def __format__(self, format_spec: str = '') -> str:
        match format_spec:
            case 'dms':
                return _format_dms(self.__value, self.hemisphere)
            case 'direction':
                return f'{abs(self.__value):g}° {self.hemisphere}'
            case _:
                return format(self.__value, format_spec)

    def __float__(self) -> float:
        return self.__value

    def __int__(self) -> int:
        return int(self.__value)

    def __bool__(self) -> bool:
        return self.__value != 0.0

    def __hash__(self) -> int:
        return hash(self.__value)

    def _other_value(self, other: str | Numeric | Longitude) -> float:
        return parse_longitude(other, 'other')

    def __add__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self.__value + self._other_value(other))

    def __radd__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self._other_value(other) + self.__value)

    def __iadd__(self, other: str | Numeric | Longitude) -> Self:
        self.__value = parse_longitude(self.__value + self._other_value(other), classname(self))
        return self

    def __sub__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self.__value - self._other_value(other))

    def __rsub__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self._other_value(other) - self.__value)

    def __isub__(self, other: str | Numeric | Longitude) -> Self:
        self.__value = parse_longitude(self.__value - self._other_value(other), classname(self))
        return self

    def __mul__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self.__value * self._other_value(other))

    def __rmul__(self, other: str | Numeric | Longitude) -> Longitude:
        return type(self)(self._other_value(other) * self.__value)

    def __imul__(self, other: str | Numeric | Longitude) -> Self:
        self.__value = parse_longitude(self.__value * self._other_value(other), classname(self))
        return self

    def __truediv__(self, other: str | Numeric | Longitude) -> Longitude:
        other_value: float = self._other_value(other)
        if other_value == 0.0:
            raise ZeroDivisionError('Cannot divide a longitude by zero')
        return type(self)(self.__value / other_value)

    def __rtruediv__(self, other: str | Numeric | Longitude) -> Longitude:
        if self.__value == 0.0:
            raise ZeroDivisionError('Cannot divide by a longitude with value zero')
        return type(self)(self._other_value(other) / self.__value)

    def __itruediv__(self, other: str | Numeric | Longitude) -> Self:
        other_value: float = self._other_value(other)
        if other_value == 0.0:
            raise ZeroDivisionError('Cannot divide a longitude by zero')
        self.__value = parse_longitude(self.__value / other_value, classname(self))
        return self

    def __neg__(self) -> Longitude:
        return type(self)(-self.__value)

    def __pos__(self) -> Longitude:
        return type(self)(+self.__value)

    def __abs__(self) -> Longitude:
        return type(self)(abs(self.__value))

    def __round__(self, ndigits: int | None = None) -> Longitude:
        return type(self)(round(self.__value, ndigits))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Longitude):
            return self.__value == other.value

        if isinstance(other, (str, int, float, Decimal)) and not isinstance(other, bool):
            try:
                return self.__value == parse_longitude(other, 'other')
            except (TypeError, ValueError):
                return False
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: str | Numeric | Longitude) -> bool:
        return self.__value < self._other_value(other)

    def __le__(self, other: str | Numeric | Longitude) -> bool:
        return self.__value <= self._other_value(other)

    def __gt__(self, other: str | Numeric | Longitude) -> bool:
        return self.__value > self._other_value(other)

    def __ge__(self, other: str | Numeric | Longitude) -> bool:
        return self.__value >= self._other_value(other)

    def __copy__(self) -> Longitude:
        return type(self)(self.__value)

    def to_dms(self) -> tuple[int, int, float]:
        absolute_value: float = abs(self.__value)
        degrees: int = int(absolute_value)
        total_minutes: float = (absolute_value - degrees) * 60
        minutes: int = int(total_minutes)
        seconds: float = (total_minutes - minutes) * 60
        return degrees, minutes, seconds

    @staticmethod
    @parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, Longitude))
    def validate(value: str | Numeric | Longitude) -> bool:
        try:
            parse_longitude(value, 'Longitude')
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    @parser_cache(skip_when=lambda cls, value, *args, **kwargs: isinstance(value, Longitude))
    def parse(cls, value: str | Numeric | Longitude) -> Longitude | None:
        parsed_value: float = parse_longitude(value, classname(cls))
        return cls(parsed_value, _skip_parser=True)

    @classmethod
    def findall(cls, text: str) -> list[Longitude]:
        Assertion(text).must_be(str)
        return [cls(match.group('longitude')) for match in longitude_pattern.finditer(text)]

    @property
    def value(self) -> float:
        return self.__value

    @property
    def degrees(self) -> float:
        return self.__value

    @property
    def hemisphere(self) -> Literal['E', 'W']:
        return 'E' if self.__value >= 0.0 else 'W'


class Coordinate(DType):
    EARTH_RADIUS_KM = 6371.0088

    @overload
    def __init__(self, coords: CoordinateTuple) -> None: ...

    @overload
    def __init__(self, lat: str | Numeric | Latitude, lon: str | Numeric | Longitude) -> None: ...

    def __init__(self, coords_or_lat: CoordinateInitInput, lon: str | Numeric | Longitude | None = None) -> None:
        self.__latitude: Latitude
        self.__longitude: Longitude
        latitude_value: float
        longitude_value: float

        if isinstance(coords_or_lat, list | tuple):
            if len(coords_or_lat) != 2:
                raise ValueError(
                    f'{classname(self)} must contain exactly two values '
                    f'(latitude, longitude), got {len(coords_or_lat)}'
                )
            latitude_value = parse_latitude(coords_or_lat[0], f'{classname(self)}.latitude')
            longitude_value = parse_longitude(coords_or_lat[1], f'{classname(self)}.longitude')
            self.__latitude = Latitude(latitude_value, _skip_parser=True)
            self.__longitude = Longitude(longitude_value, _skip_parser=True)
            return

        if lon is None:
            latitude_value, longitude_value = parse_coordinate(coords_or_lat, classname(self))
        else:
            latitude_value = parse_latitude(coords_or_lat, f'{classname(self)}.latitude')
            longitude_value = parse_longitude(lon, f'{classname(self)}.longitude')

        self.__latitude = Latitude(latitude_value, _skip_parser=True)
        self.__longitude = Longitude(longitude_value, _skip_parser=True)

    def __str__(self) -> str:
        return f'{self.__latitude}, {self.__longitude}'

    def __repr__(self) -> str:
        return f'{classname(self)}({self.__latitude.value!r}, {self.__longitude.value!r})'

    def __format__(self, format_spec: str = '') -> str:
        match format_spec:
            case '' | 'csv':
                return str(self)
            case 'tuple':
                return repr(self.value)
            case 'latitude' | 'lat':
                return format(self.__latitude, '')
            case 'longitude' | 'lon' | 'lng':
                return format(self.__longitude, '')
            case 'direction' | 'cardinal':
                return f'{self.__latitude:direction}, {self.__longitude:direction}'
            case _:
                return f'{self.__latitude:{format_spec}}, {self.__longitude:{format_spec}}'

    def __iter__(self) -> Iterator[float]:
        return iter(self.value)

    def __len__(self) -> int:
        return 2

    def __getitem__(self, item: int | Literal['latitude', 'longitude', 'lat', 'lon', 'lng']) -> float:
        match item:
            case 0 | 'latitude' | 'lat':
                return self.__latitude.value
            case 1 | 'longitude' | 'lon' | 'lng':
                return self.__longitude.value
            case _:
                raise IndexError(f'Coordinate has no item {item!r}')

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Coordinate):
            return self.value == other.value
        if isinstance(other, (str, tuple, list)):
            try:
                return self.value == parse_coordinate(other, 'other')
            except (TypeError, ValueError):
                return False
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __add__(self, other: CoordinateInput) -> Coordinate:
        other_coordinate: Coordinate = Coordinate(other)
        return Coordinate(
            self.__latitude.value + other_coordinate.latitude.value,
            self.__longitude.value + other_coordinate.longitude.value,
        )

    def __sub__(self, other: CoordinateInput) -> Coordinate:
        other_coordinate: Coordinate = Coordinate(other)
        return Coordinate(
            self.__latitude.value - other_coordinate.latitude.value,
            self.__longitude.value - other_coordinate.longitude.value,
        )

    def __copy__(self) -> Coordinate:
        return type(self)(self.value)

    @staticmethod
    @parser_cache(skip_when=lambda value, *args, **kwargs: isinstance(value, (list, Coordinate)))
    def validate(value: CoordinateInput) -> bool:
        try:
            parse_coordinate(value, classname(value))
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    @parser_cache(skip_when=lambda cls, value, *args, **kwargs: isinstance(value, (list, Coordinate)))
    def parse(cls, value: CoordinateInput) -> Coordinate | None:
        parsed_value: tuple[float, float] = parse_coordinate(value, classname(cls))
        return cls(parsed_value)

    @classmethod
    def findall(cls, text: str) -> list[Coordinate]:
        Assertion(text).must_be(str)
        return [cls(match.group(0)) for match in coordinate_pattern.finditer(text)]

    @classmethod
    def from_values(
        cls,
        latitude: str | Numeric | Latitude,
        longitude: str | Numeric | Longitude,
    ) -> Coordinate:
        return cls(latitude, longitude)

    @classmethod
    def from_radians(cls, latitude: float, longitude: float) -> Coordinate:
        return cls(math.degrees(latitude), math.degrees(longitude))

    def offset(
        self,
        latitude_delta: str | Numeric | Latitude,
        longitude_delta: str | Numeric | Longitude,
    ) -> Coordinate:
        new_latitude: float = self.latitude.value + parse_latitude(latitude_delta, 'latitude_delta')
        new_longitude: float = self.longitude.value + parse_longitude(longitude_delta, 'longitude_delta')
        return type(self)(new_latitude, new_longitude)

    def distance_to(
        self,
        other: CoordinateInput,
        unit: Literal['km', 'kilometers', 'm', 'meters', 'mi', 'miles'] = 'km',
    ) -> float:
        other_coordinate: Coordinate = Coordinate(other)
        latitude_1: float
        longitude_1: float
        latitude_1, longitude_1 = self.to_radians()
        latitude_2: float
        longitude_2: float
        latitude_2, longitude_2 = other_coordinate.to_radians()

        delta_latitude: float = latitude_2 - latitude_1
        delta_longitude: float = longitude_2 - longitude_1
        haversine: float = (
            math.sin(delta_latitude / 2) ** 2
            + math.cos(latitude_1)
            * math.cos(latitude_2)
            * math.sin(delta_longitude / 2) ** 2
        )
        distance_km: float = self.EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(haversine))

        match unit:
            case 'km' | 'kilometers':
                return distance_km
            case 'm' | 'meters':
                return distance_km * 1000
            case 'mi' | 'miles':
                return distance_km * 0.621371192237334
            case _:
                raise ValueError(f'Unknown distance unit: {unit!r}')

    def bearing_to(self, other: CoordinateInput) -> float:
        other_coordinate: Coordinate = Coordinate(other)
        latitude_1: float
        longitude_1: float
        latitude_1, longitude_1 = self.to_radians()
        latitude_2: float
        longitude_2: float
        latitude_2, longitude_2 = other_coordinate.to_radians()

        delta_longitude: float = longitude_2 - longitude_1
        y: float = math.sin(delta_longitude) * math.cos(latitude_2)
        x: float = (
            math.cos(latitude_1) * math.sin(latitude_2)
            - math.sin(latitude_1)
            * math.cos(latitude_2)
            * math.cos(delta_longitude)
        )
        return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

    def midpoint_to(self, other: CoordinateInput) -> Coordinate:
        other_coordinate: Coordinate = Coordinate(other)
        latitude_1: float
        longitude_1: float
        latitude_1, longitude_1 = self.to_radians()
        latitude_2: float
        longitude_2: float
        latitude_2, longitude_2 = other_coordinate.to_radians()

        x: float = math.cos(latitude_2) * math.cos(longitude_2)
        y: float = math.cos(latitude_2) * math.sin(longitude_2)
        z: float = math.sin(latitude_2)
        x += math.cos(latitude_1) * math.cos(longitude_1)
        y += math.cos(latitude_1) * math.sin(longitude_1)
        z += math.sin(latitude_1)

        longitude: float = math.atan2(y, x)
        hypotenuse: float = math.sqrt(x * x + y * y)
        latitude: float = math.atan2(z, hypotenuse)
        return type(self).from_radians(latitude, longitude)

    def within(
        self,
        other: CoordinateInput,
        radius: float,
        unit: Literal['km', 'kilometers', 'm', 'meters', 'mi', 'miles'] = 'km',
    ) -> bool:
        if radius < 0:
            raise ValueError(f'radius must be non-negative, got {radius}')
        return self.distance_to(other, unit) <= radius

    def to_radians(self) -> tuple[float, float]:
        return math.radians(self.__latitude.value), math.radians(self.__longitude.value)

    @property
    def value(self) -> tuple[float, float]:
        return self.__latitude.value, self.__longitude.value

    @property
    def latitude(self) -> Latitude:
        return self.__latitude

    @property
    def longitude(self) -> Longitude:
        return self.__longitude

    @property
    def lat(self) -> Latitude:
        return self.__latitude

    @property
    def lon(self) -> Longitude:
        return self.__longitude

    @property
    def lng(self) -> Longitude:
        return self.__longitude

type CoordinateTuple = (
    list[str | Numeric | Latitude | Longitude]
    | tuple[str | Numeric | Latitude | Longitude, str | Numeric | Latitude | Longitude]
)
type CoordinateInitInput = (
    str
    | CoordinateTuple
    | Coordinate
    | Numeric
    | Latitude
    | Longitude
)
type CoordinateInput = (
    str
    | CoordinateTuple
    | Coordinate
)
