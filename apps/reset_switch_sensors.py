from __future__ import annotations

from datetime import timedelta
from typing import Any

from base_app import BaseApp
import curve
from switch import HueDimmerSwitch, ALL_SWITCHES


class ResetSwitchSensors(BaseApp):
    async def initialize(self) -> None:
        morning_time, _ = curve.points[1]
        self.run_daily(self.reset_switch_sensors, morning_time)

    async def reset_switch_sensors(self, kwargs: dict[str, Any]) -> None:
        try:
            for switch in ALL_SWITCHES:
                switch.sensor.set_state(self, HueDimmerSwitch.State.DEFAULT)
        except:
            self.notify_exception()
            raise
