from __future__ import annotations

from datetime import datetime, time

from appdaemon.plugins.hass.hassapi import Hass

import numpy as np
from scipy.interpolate import pchip  # type: ignore[import]

from light_setting import LightSetting


def time_to_minutes_since_midnight(time: time) -> int:
    return time.hour * 60 + time.minute


def kelvin_to_mireds(kelvin: int) -> int:
    return int(round(1_000_000 / kelvin))


def mireds_to_kelvin(mireds: int) -> int:
    return kelvin_to_mireds(mireds)


# Points to interpolate between

points = [
    (
        time(0, 00),
        LightSetting(brightness=0, color_temperature=kelvin_to_mireds(2000)),
    ),
    (
        time(6, 00),
        LightSetting(brightness=0, color_temperature=kelvin_to_mireds(2000)),
    ),
    (
        time(6, 30),
        LightSetting(brightness=255, color_temperature=kelvin_to_mireds(6500)),
    ),
    (
        time(8, 00),
        LightSetting(brightness=255, color_temperature=kelvin_to_mireds(5500)),
    ),
    (
        time(12, 00),
        LightSetting(brightness=255, color_temperature=kelvin_to_mireds(5000)),
    ),
    (
        time(17, 00),
        LightSetting(brightness=255, color_temperature=kelvin_to_mireds(4500)),
    ),
    (
        time(20, 00),
        LightSetting(brightness=100, color_temperature=kelvin_to_mireds(3000)),
    ),
    (
        time(23, 15),
        LightSetting(brightness=10, color_temperature=kelvin_to_mireds(2200)),
    ),
    (
        time(23, 45),
        LightSetting(brightness=1, color_temperature=kelvin_to_mireds(2000)),
    ),
    (
        time(23, 59),
        LightSetting(brightness=0, color_temperature=kelvin_to_mireds(2000)),
    ),
]


# Split points into lists of x and y coordinates

time_values = np.array([time_to_minutes_since_midnight(time) for time, _ in points])

brightness_values = np.array([light_setting.brightness for _, light_setting in points])

color_temperature_values = np.array(
    [light_setting.color_temperature for _, light_setting in points]
)

# Interpolate monotonic cubic splines between points

brightness_curve = pchip(time_values, brightness_values)

color_temperature_curve = pchip(time_values, color_temperature_values)


async def current_light_setting(app: Hass) -> LightSetting:
    minutes_since_midnight = time_to_minutes_since_midnight(await app.time())

    return LightSetting(
        brightness=int(brightness_curve(minutes_since_midnight)),
        color_temperature=int(color_temperature_curve(minutes_since_midnight)),
    )
