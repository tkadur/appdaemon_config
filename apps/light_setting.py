from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass(frozen=True)
class LightSetting:
    brightness: int
    color_temperature: int

    OFF: ClassVar[LightSetting]

    def __post_init__(self) -> None:
        assert (
            0 <= self.brightness and self.brightness <= 255
        ), f"Brightness {self.brightness} must be within the range [0, 255]."

        assert (
            153 <= self.color_temperature and self.color_temperature <= 500
        ), f"Color temperature {self.color_temperature}M must be within the range [153M, 500M]."

    def with_brightness(self, new_brightness: int) -> LightSetting:
        return LightSetting(
            brightness=new_brightness, color_temperature=self.color_temperature
        )


LightSetting.OFF = LightSetting(brightness=0, color_temperature=153)
