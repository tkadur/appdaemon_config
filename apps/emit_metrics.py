from __future__ import annotations

from datetime import time
import functools
from typing import Any

from base_app import BaseApp
from curve import current_curve_setting
from metrics import Metric
from light_setting import LightSetting
from lights import Room, home


class EmitMetrics(BaseApp):
    def initialize(self) -> None:
        self.run_minutely(self._default_brightness().mk_update(self), time(second=30))

        for room in home.rooms:
            self.run_minutely(
                self._room_brightness(room).mk_update(self), time(second=30)
            )

        self.run_minutely(self._color_temperature().mk_update(self), time(second=30))

    def _default_brightness(self) -> Metric:
        async def calculate() -> Metric.Value:
            current_setting = await current_curve_setting(self)
            return Metric.Value(current_setting.brightness, {"source": "Default"})

        return Metric(
            name="brightness",
            unit_of_measurement="%",
            calculate=calculate,
        )

    def _room_brightness(self, room: Room) -> Metric:
        async def calculate() -> Metric.Value:
            current_setting = await room.current_setting(self)
            return Metric.Value(
                current_setting.brightness, {"source": room.readable_name}
            )

        return Metric(
            name="brightness",
            unit_of_measurement="%",
            calculate=calculate,
        )

    def _color_temperature(self) -> Metric:
        async def calculate() -> Metric.Value:
            current_setting = await current_curve_setting(self)
            return Metric.Value(current_setting.color_temperature)

        return Metric(
            name="color_temperature",
            unit_of_measurement="K",
            calculate=calculate,
        )
