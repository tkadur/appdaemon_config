from __future__ import annotations

from datetime import time
from typing import Any

from lights import home

from base_app import BaseApp
from curve import current_light_setting


class TimeBasedColor(BaseApp):
    async def initialize(self) -> None:
        self.run_minutely(self.set_lights_timer, time(second=0))
        self.listen_state(self.set_lights_switch, "switch")

        self.current_setting = await current_light_setting(self)

    async def set_lights_timer(self, kwargs: dict[str, Any]) -> None:
        await self._set_lights()

    async def set_lights_switch(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict[str, Any]
    ) -> None:
        await self._set_lights()

    async def _set_lights(self) -> None:
        try:
            new_setting = await current_light_setting(self)
            if self.current_setting == new_setting:
                self.log("Skipping minutely update")
                return

            await home.refresh(self)
        except:
            self.notify_exception()
            raise
