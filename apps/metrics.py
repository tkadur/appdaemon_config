from collections.abc import Coroutine
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, Protocol

from appdaemon.plugins.hass.hassapi import Hass

from curve import current_light_setting, mireds_to_kelvin

# Workaround https://github.com/python/mypy/issues/5485 until the fix
# gets info the next mypy release
class CalculateFn(Protocol):
    def __call__(self, app: Hass) -> Coroutine[None, None, int]:
        ...


@dataclass(frozen=True)
class Metric:
    name: str
    unit_of_measurement: str
    calculate: CalculateFn

    @cached_property
    def _entity_name(self) -> str:
        return f"metric.{self.name}"

    def mk_update(
        self, app: Hass
    ) -> Callable[[dict[str, Any]], Coroutine[None, None, None]]:
        async def update(kwargs: dict[str, Any]) -> None:
            await app.set_state(
                self._entity_name,
                state=await self.calculate(app),
                attributes={"unit_of_measurement": self.unit_of_measurement},
            )

        return update


def brightness_metric() -> Metric:
    # Convert from a 0-255 scale to a 0-100 scale
    async def calculate(app: Hass) -> int:
        current_brightness = (await current_light_setting(app)).brightness
        return int(round(current_brightness / 255))

    return Metric(
        name="brightness",
        unit_of_measurement="%",
        calculate=calculate,
    )


def color_temperature_metric() -> Metric:
    async def calculate(app: Hass) -> int:
        current_color_temperature = (await current_light_setting(app)).color_temperature
        return mireds_to_kelvin(current_color_temperature)

    return Metric(
        name="color_temperature",
        unit_of_measurement="K",
        calculate=calculate,
    )
