from __future__ import annotations

from collections.abc import Coroutine
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, Protocol

from appdaemon.plugins.hass.hassapi import Hass

# Workaround https://github.com/python/mypy/issues/5485 until the fix
# gets info the next mypy release
class CalculateFn(Protocol):
    def __call__(self) -> Coroutine[None, None, Metric.Value]:
        ...


@dataclass(frozen=True)
class Metric:
    name: str
    unit_of_measurement: str
    calculate: CalculateFn

    @cached_property
    def _entity_name(self) -> str:
        return f"metric.{self.name}"

    @dataclass(frozen=True)
    class Value:
        state: int
        extra_attributes: dict[str, int | str] = field(default_factory=dict)

    def mk_update(
        self, app: Hass
    ) -> Callable[[dict[str, Any]], Coroutine[None, None, None]]:
        async def update(kwargs: dict[str, Any]) -> None:
            value = await self.calculate()
            await app.set_state(
                self._entity_name,
                state=value.state,
                attributes={
                    "unit_of_measurement": self.unit_of_measurement,
                    **value.extra_attributes,
                },
            )

        return update
