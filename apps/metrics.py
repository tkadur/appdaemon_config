from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, Protocol

from appdaemon.plugins.hass.hassapi import Hass

from curve import current_light_setting

# Workaround https://github.com/python/mypy/issues/5485 until the fix
# gets info the next mypy release
class CalculateFn(Protocol):
    def __call__(self, hass: Hass) -> int:
        ...


@dataclass(frozen=True)
class Metric:
    name: str
    unit_of_measurement: str
    calculate: CalculateFn

    @cached_property
    def _entity_name(self) -> str:
        return f"metric.{self.name}"

    def mk_update(self, hass: Hass) -> Callable[[dict[str, Any]], None]:
        return lambda _: hass.set_state(
            self._entity_name,
            state=self.calculate(hass),
            attributes={"unit_of_measurement": self.unit_of_measurement},
        )


def brightness_metric(hass: Hass) -> Metric:
    return Metric(
        name="brightness",
        unit_of_measurement="%",
        calculate=lambda hass: current_light_setting(hass).brightness,
    )


def color_temperature_metric(hass: Hass) -> Metric:
    return Metric(
        name="color_temperature",
        unit_of_measurement="K",
        calculate=lambda hass: current_light_setting(hass).color_temperature,
    )
