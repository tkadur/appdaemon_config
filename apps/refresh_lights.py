from __future__ import annotations

from datetime import time
from typing import Any

from lights import home, bedroom

from base_app import BaseApp
from curve import current_curve_setting


class RefreshLights(BaseApp):
    async def initialize(self) -> None:
        self.run_minutely(self.refresh_lights_timer, time(second=0))
        self.listen_state(self.refresh_lights_switch, "switch")

    async def refresh_lights_timer(self, kwargs: dict[str, Any]) -> None:
        try:
            await home.refresh(self)
        except:
            self.notify_exception()
            raise

    async def refresh_lights_switch(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict[str, Any]
    ) -> None:
        try:
            # Only refresh rooms controlled by the pressed switch
            for room in home.rooms:
                if room.switch_sensor.entity_id == entity:
                    await room.refresh(self)
        except:
            self.notify_exception()
            raise
