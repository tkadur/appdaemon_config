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
    async def calculate(app: Hass) -> int:
        current_setting = await current_light_setting(app)
        # Display the metric on a 0-100 scale instead of 0-255
        return int(round(current_setting.brightness / 2.55))

    return Metric(
        name="brightness",
        unit_of_measurement="%",
        calculate=calculate,
    )


def color_temperature_metric() -> Metric:
    async def calculate(app: Hass) -> int:
        current_setting = await current_light_setting(app)
        return mireds_to_kelvin(current_setting.color_temperature)

    return Metric(
        name="color_temperature",
        unit_of_measurement="K",
        calculate=calculate,
    )
