from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LightSetting:
    brightness: int
    color_temperature: int

    def __post_init__(self) -> None:
        assert (
            0 <= self.brightness and self.brightness <= 100
        ), f"Brightness {self.brightness} must be within the range [0, 100]."

        assert (
            2200 <= self.color_temperature and self.color_temperature <= 6500
        ), f"Color temperature {self.color_temperature}K must be within the range [2200K, 6500K]."

    @staticmethod
    def off() -> LightSetting:
        return LightSetting(brightness=0, color_temperature=2200)

    def with_brightness(self, new_brightness: int) -> LightSetting:
        return LightSetting(
            brightness=new_brightness, color_temperature=self.color_temperature
        )

    def with_color_temperature(self, new_color_temperature: int) -> LightSetting:
        return LightSetting(
            brightness=self.brightness, color_temperature=new_color_temperature
        )