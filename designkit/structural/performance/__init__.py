"""Adaptive performance utilities for selecting work for the current machine."""

from designkit.structural.performance.core import (
    AdaptiveFunction,
    PerformanceContext,
    PerformancePreset,
    PresetSettings,
    SystemProfile,
    adaptive,
    detect_preset,
    get_system_profile,
    preset_settings,
)

__all__ = [
    'AdaptiveFunction',
    'PerformanceContext',
    'PerformancePreset',
    'PresetSettings',
    'SystemProfile',
    'adaptive',
    'detect_preset',
    'get_system_profile',
    'preset_settings',
]