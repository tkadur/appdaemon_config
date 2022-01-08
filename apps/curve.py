from __future__ import annotations

from datetime import datetime, time

from appdaemon.plugins.hass.hassapi import Hass

import numpy as np
from scipy.interpolate import pchip  # type: ignore[import]

from light_setting import LightSetting


def time_to_minutes_since_midnight(time: time) -> int:
    return time.hour * 60 + time.minute


# Points to interpolate between

points = [
    (
        time(0, 00),
        LightSetting(brightness=0, color_temperature=2000),
    ),
    (
        time(7, 30),
        LightSetting(brightness=0, color_temperature=2000),
    ),
    (
        time(8, 00),
        LightSetting(brightness=100, color_temperature=6500),
    ),
    (
        time(8, 30),
        LightSetting(brightness=100, color_temperature=5500),
    ),
    (
        time(12, 00),
        LightSetting(brightness=100, color_temperature=5000),
    ),
    (
        time(17, 00),
        LightSetting(brightness=100, color_temperature=4500),
    ),
    (
        time(20, 00),
        LightSetting(brightness=50, color_temperature=3000),
    ),
    (
        time(23, 15),
        LightSetting(brightness=6, color_temperature=2200),
    ),
    (
        time(23, 58),
        LightSetting(brightness=1, color_temperature=2000),
    ),
    (
        time(23, 59),
        LightSetting(brightness=0, color_temperature=2000),
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


async def current_curve_setting(app: Hass) -> LightSetting:
    minutes_since_midnight = time_to_minutes_since_midnight(await app.time())

    return LightSetting(
        brightness=int(brightness_curve(minutes_since_midnight)),
        color_temperature=int(color_temperature_curve(minutes_since_midnight)),
    )
