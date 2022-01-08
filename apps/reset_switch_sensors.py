from __future__ import annotations

from datetime import time
from typing import Any

from base_app import BaseApp
from switch import HueDimmerSwitch, ALL_SWITCHES


class ResetSwitchSensors(BaseApp):
    def initialize(self) -> None:
        self.run_daily(self.reset_switch_sensors, time(5, 00))

    def reset_switch_sensors(self, kwargs: dict[str, Any]) -> None:
        try:
            for switch in ALL_SWITCHES:
                switch.sensor.set_state(self, switch.sensor.default_state)
        except:
            self.notify_exception()
            raise
