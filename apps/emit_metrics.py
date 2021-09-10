from __future__ import annotations

from datetime import time
from typing import Any

from metrics import brightness_metric, color_temperature_metric

from base_app import BaseApp


class EmitMetrics(BaseApp):
    def initialize(self) -> None:
        self.brightness_metric = brightness_metric(self)
        self.run_minutely(self.brightness_metric.mk_update(self), time(second=0))

        self.color_temperature_metric = color_temperature_metric(self)
        self.run_minutely(self.color_temperature_metric.mk_update(self), time(second=0))
