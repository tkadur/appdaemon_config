from __future__ import annotations

from typing import Any

from base_app import BaseApp
import curve
from lights import home
from switch import HueDimmerSwitch, all_switches


class ResetSwitchesEveryNight(BaseApp):
    def initialize(self) -> None:
        morning_time, _ = curve.points[1]
        self.run_daily(self.reset_switches, morning_time)

    def reset_switches(self, kwargs: dict[str, Any]) -> None:
        try:
            for switch in all_switches:
                switch.set_state(self, HueDimmerSwitch.State.DEFAULT)
            home.refresh(self)
        except:
            self.notify_exception()
            raise
