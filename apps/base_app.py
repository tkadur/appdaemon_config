from collections.abc import Coroutine
import traceback
from typing import Any, Iterable

from appdaemon.plugins.hass.hassapi import Hass, hass_check
import appdaemon.utils

from exceptions import LightUnresponsiveException
from light_setting import LightSetting
from util import PredicateBackoffDetails


class BaseApp(Hass):
    def notify_exception(self) -> None:
        self.notify("Encountered the following exception: \n" + traceback.format_exc())

    @appdaemon.utils.sync_wrapper
    @hass_check
    async def set_light(self, entity_id: str, setting: LightSetting) -> None:

        if setting.brightness == 0:
            await self.turn_off(entity_id=entity_id)
        else:
            await self.turn_on(
                entity_id=entity_id,
                brightness=setting.brightness,
                color_temp=setting.color_temperature,
            )

