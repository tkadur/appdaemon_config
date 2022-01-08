import traceback
from typing import Any, Iterable

from appdaemon.plugins.hass.hassapi import Hass, hass_check
import appdaemon.utils

from light_setting import LightSetting


class BaseApp(Hass):
    def notify_exception(self) -> None:
        self.notify("Encountered the following exception: \n" + traceback.format_exc())

    def set_light(self, entity_id: str, setting: LightSetting) -> None:
        if setting.brightness == 0:
            self.turn_off(entity_id=entity_id)
        else:
            self.turn_on(
                entity_id=entity_id,
                brightness_pct=setting.brightness,
                kelvin=setting.color_temperature,
            )
