from __future__ import annotations

from datetime import time
from typing import Any

from lights import home

from base_app import BaseApp
from curve import current_light_setting


class TimeBasedColor(BaseApp):
    async def initialize(self) -> None:
        self.run_minutely(self.refresh_lights_timer, time(second=0))
        self.listen_state(self.refresh_lights_switch, "switch")

        self.current_setting = await current_light_setting(self)

    async def refresh_lights_timer(self, kwargs: dict[str, Any]) -> None:
        await self._refresh_lights()

    async def refresh_lights_switch(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict[str, Any]
    ) -> None:
        self.log("Received switch event")
        await self._refresh_lights()

    async def _refresh_lights(self) -> None:
        try:
            await home.refresh(self)
        except:
            self.notify_exception()
            raise
