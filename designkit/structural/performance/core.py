
import ctypes
import os, sys, platform
from dataclasses import dataclass
from enum import Enum
from functools import update_wrapper
from types import MethodType
from typing import Callable, Mapping, Self

type Callback[P, R] = Callable[[P], R]
MNEMENIC_GIB: int = 1024**3
MNEMENIC_MIB: int = 1024**2


class PerformancePreset(str, Enum):
    """Execution levels ordered from the most conservative to the most capable."""

    LIGHT = 'light'
    BALANCED = 'balanced'
    HEAVY = 'heavy'

    @classmethod
    def coerce(cls, value: Self | str) -> Self:
        if isinstance(value, cls):
            return value

        try:
            return cls(value.lower())
        except (AttributeError, ValueError) as error:
            valid = ', '.join(preset.value for preset in cls)
            raise ValueError(
                f'Invalid performance preset {value!r}; expected one of: {valid}'
            ) from error


@dataclass(frozen=True, slots=True)
class SystemProfile:
    """Capabilities detected from the host running the Python process.

    ``logical_cores`` is constrained to the CPUs available to the process, so
    the value also behaves correctly inside containers and restricted workers.
    ``physical_cores`` and ``memory_bytes`` are optional because some operating
    systems do not expose them through the standard library.
    """

    logical_cores: int
    physical_cores: int | None
    memory_bytes: int | None
    system: str
    architecture: str
    processor: str
    python_version: str

    def __post_init__(self) -> None:
        if self.logical_cores < 1:
            raise ValueError('logical_cores must be greater than zero')
        if self.physical_cores is not None and self.physical_cores < 1:
            raise ValueError('physical_cores must be greater than zero')
        if self.memory_bytes is not None and self.memory_bytes < 1:
            raise ValueError('memory_bytes must be greater than zero')

    @classmethod
    def detect(cls) -> Self:
        """Read the host capabilities without third-party dependencies."""

        return cls(
            logical_cores=_available_cpu_count(),
            physical_cores=_physical_cpu_count(),
            memory_bytes=_total_memory_bytes(),
            system=platform.system() or 'Unknown',
            architecture=platform.machine() or 'Unknown',
            processor=platform.processor() or 'Unknown',
            python_version=platform.python_version(),
        )

    @property
    def memory_gib(self) -> float | None:
        return None if self.memory_bytes is None else self.memory_bytes / MNEMENIC_GIB

    @property
    def core_count(self) -> int:
        """Alias for the process-visible logical core count."""

        return self.logical_cores

    def as_dict(self) -> dict[str, int | float | str | None]:
        """Return a serialization-friendly representation of the profile."""

        return {
            'logical_cores': self.logical_cores,
            'physical_cores': self.physical_cores,
            'memory_bytes': self.memory_bytes,
            'memory_gib': self.memory_gib,
            'system': self.system,
            'architecture': self.architecture,
            'processor': self.processor,
            'python_version': self.python_version,
        }


@dataclass(frozen=True, slots=True)
class PresetSettings:
    """Conservative limits associated with a performance preset."""

    preset: PerformancePreset
    max_workers: int
    chunk_size: int
    max_items: int | None

    def __post_init__(self) -> None:
        if self.max_workers < 1:
            raise ValueError('max_workers must be greater than zero')
        if self.chunk_size < 1:
            raise ValueError('chunk_size must be greater than zero')
        if self.max_items is not None and self.max_items < 1:
            raise ValueError('max_items must be greater than zero')


@dataclass(frozen=True, slots=True)
class PerformanceContext:
    """A detected profile together with the preset selected for it."""

    profile: SystemProfile
    preset: PerformancePreset

    @classmethod
    def detect(cls, profile: SystemProfile | None = None) -> Self:
        profile = profile or SystemProfile.detect()
        return cls(profile=profile, preset=detect_preset(profile))

    @classmethod
    def for_preset(
        cls,
        preset: PerformancePreset | str,
        profile: SystemProfile | None = None,
    ) -> Self:
        return cls(
            profile=profile or SystemProfile.detect(),
            preset=PerformancePreset.coerce(preset),
        )

    @property
    def settings(self) -> PresetSettings:
        return preset_settings(self.preset, self.profile)


def get_system_profile() -> SystemProfile:
    """Detect and return the current computer capabilities."""

    return SystemProfile.detect()


def detect_preset(profile: SystemProfile) -> PerformancePreset:
    """Choose a safe preset using process-visible cores and available memory.

    Heavy work is only selected when the machine has more than four logical
    cores and more than eight GiB of memory. This intentionally conservative
    rule keeps older or low-memory computers away from the expensive variant.
    """

    processor = profile.processor.casefold()
    if any(name in processor for name in ('pentium', 'celeron', 'atom')):
        return PerformancePreset.LIGHT

    if profile.logical_cores <= 2:
        return PerformancePreset.LIGHT
    if profile.memory_gib is not None and profile.memory_gib <= 4:
        return PerformancePreset.LIGHT
    if profile.logical_cores <= 4:
        return PerformancePreset.BALANCED
    if profile.memory_gib is None or profile.memory_gib <= 8:
        return PerformancePreset.BALANCED
    return PerformancePreset.HEAVY


def preset_settings(
    preset: PerformancePreset | str,
    profile: SystemProfile | None = None,
) -> PresetSettings:
    """Build execution limits for a preset and a particular host profile."""

    preset = PerformancePreset.coerce(preset)
    profile = profile or SystemProfile.detect()

    if preset is PerformancePreset.LIGHT:
        return PresetSettings(
            preset=preset,
            max_workers=1,
            chunk_size=64,
            max_items=10_000,
        )
    if preset is PerformancePreset.BALANCED:
        return PresetSettings(
            preset=preset,
            max_workers=min(4, profile.logical_cores),
            chunk_size=256,
            max_items=100_000,
        )
    return PresetSettings(
        preset=preset,
        max_workers=max(1, profile.logical_cores - 1),
        chunk_size=1_024,
        max_items=None,
    )


class AdaptiveFunction[P, R]:
    """Callable that dispatches to exactly one implementation per invocation."""

    def __init__(
        self,
        function: Callback,
        variants: Mapping[PerformancePreset, Callback],
        context: PerformanceContext,
    ) -> None:
        self.__function: Callback = function
        self.__variants: Mapping[PerformancePreset, Callback] = dict(variants)
        self.__context: PerformanceContext = context
        update_wrapper(self, function)

    @property
    def context(self) -> PerformanceContext:
        return self.__context

    @property
    def profile(self) -> SystemProfile:
        return self.__context.profile

    @property
    def preset(self) -> PerformancePreset:
        return self.__context.preset

    @property
    def settings(self) -> PresetSettings:
        return self.__context.settings

    def refresh(self, profile: SystemProfile | None = None) -> Self:
        """Re-detect the host after a process migration or resource change."""

        self.__context = PerformanceContext.detect(profile)
        return self

    def with_preset(
        self,
        preset: PerformancePreset | str,
    ) -> Callback:
        """Return one implementation for explicit tests or controlled runs."""

        selected = PerformancePreset.coerce(preset)
        return self.__variants.get(selected, self.__function)

    def implementation(self) -> Callback:
        """Return the implementation selected by the current context."""

        return self.with_preset(self.preset)

    def __call__(self, *args: P, **kwargs: P) -> R:
        return self.implementation()(*args, **kwargs)

    def __get__(
        self,
        instance: object | None,
        owner: type[object] | None = None,
    ) -> Self | MethodType:
        if instance is None:
            return self
        return MethodType(self.__call__, instance)


def adaptive[P, R](
    function: Callback | None = None,
    /,
    *,
    light: Callback | None = None,
    balanced: Callback | None = None,
    heavy: Callback | None = None,
    profile: SystemProfile | None = None,
    context: PerformanceContext | None = None,
) -> AdaptiveFunction[P, R] | Callable[[Callback], AdaptiveFunction[P, R]]:
    """
    Decorate a function with light, balanced, and heavy implementations.

    The decorated function is the fallback implementation. Only the selected
    variant is called; the other variants are not evaluated or initialized.

    Example::

        @adaptive(light=light_search, heavy=parallel_search)
        def search(items, query):
            return regular_search(items, query)

        result = search(items, query)
        quick_result = search.with_preset('light')(items, query)
    """

    variants: dict[PerformancePreset, Callback] = {}
    for preset, implementation in (
        (PerformancePreset.LIGHT, light),
        (PerformancePreset.BALANCED, balanced),
        (PerformancePreset.HEAVY, heavy),
    ):
        if implementation is not None:
            if not callable(implementation):
                raise TypeError(f'{preset.value} implementation must be callable')
            variants[preset] = implementation

    def decorate(target: Callback) -> AdaptiveFunction[P, R]:
        if not callable(target):
            raise TypeError('adaptive can only decorate a callable')
        selected__context = context or PerformanceContext.detect(profile)
        return AdaptiveFunction(target, variants, selected__context)

    if function is None:
        return decorate
    return decorate(function)


def _available_cpu_count() -> int:
    try:
        affinity = os.sched_getaffinity(0)
    except (AttributeError, OSError):
        affinity = None

    if affinity:
        return len(affinity)
    return os.cpu_count() or 1


def _physical_cpu_count() -> int | None:
    if not os.path.exists('/proc/cpuinfo'):
        return None

    pairs: set[tuple[str, str]] = set()
    physical_id: str | None = None
    core_id: str | None = None
    try:
        with open('/proc/cpuinfo', encoding='utf-8') as cpuinfo:
            for line in cpuinfo:
                if not line.strip():
                    if physical_id is not None and core_id is not None:
                        pairs.add((physical_id, core_id))
                    physical_id = None
                    core_id = None
                    continue

                key, separator, value = line.partition(':')
                if not separator:
                    continue
                if key.strip() == 'physical id':
                    physical_id = value.strip()
                elif key.strip() == 'core id':
                    core_id = value.strip()
    except OSError:
        return None

    if physical_id is not None and core_id is not None:
        pairs.add((physical_id, core_id))
    return len(pairs) or None


def _total_memory_bytes() -> int | None:
    if sys.platform == 'win32':
        return _windows_memory_bytes()

    try:
        with open('/proc/meminfo', encoding='utf-8') as meminfo:
            for line in meminfo:
                key, separator, value = line.partition(':')
                if key == 'MemTotal' and separator:
                    amount = value.strip().split()[0]
                    return int(amount) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _windows_memory_bytes() -> int | None:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ('dwLength', ctypes.c_ulong),
            ('dwMemoryLoad', ctypes.c_ulong),
            ('ullTotalPhys', ctypes.c_ulonglong),
            ('ullAvailPhys', ctypes.c_ulonglong),
            ('ullTotalPageFile', ctypes.c_ulonglong),
            ('ullAvailPageFile', ctypes.c_ulonglong),
            ('ullTotalVirtual', ctypes.c_ulonglong),
            ('ullAvailVirtual', ctypes.c_ulonglong),
            ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
        ]

    try:
        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.ullTotalPhys
    except (AttributeError, OSError):
        return None
    return None
