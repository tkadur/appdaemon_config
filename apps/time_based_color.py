from __future__ import annotations

from datetime import time
from typing import Any

from lights import home

from base_app import BaseApp


class TimeBasedColor(BaseApp):
    def initialize(self) -> None:
        self.run_minutely(self.set_lights_timer, time(second=0))
        self.listen_state(self.set_lights_switch, "switch")

    def set_lights_timer(self, kwargs: dict[str, Any]) -> None:
        self._set_lights()

    def set_lights_switch(
        self, entity: str, attribute: str, old: str, new: str, kwargs: dict[str, Any]
    ) -> None:
        self._set_lights()

    def _set_lights(self) -> None:
        try:
            home.refresh(self)
        except:
            self.notify_exception()
            raise
