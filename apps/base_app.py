from collections.abc import Coroutine
import traceback
from typing import Any

from appdaemon.plugins.hass.hassapi import Hass, hass_check
import appdaemon.utils
import backoff  # type: ignore[import]

from exceptions import LightUnresponsiveException
from light_setting import LightSetting
from util import PredicateBackoffDetails


def on_giveup(details: dict[str, Any]) -> None:
    backoff_details = PredicateBackoffDetails.parse_obj(details)

    backoff_details.args[0].log(
        f"Gave up on {backoff_details.target.__name__}("
        f"args={backoff_details.args[1:]}, kwargs={backoff_details.kwargs}"
        f") after {backoff_details.tries} tries."
    )


class BaseApp(Hass):
    def notify_exception(self) -> None:
        self.notify("Encountered the following exception: \n" + traceback.format_exc())

    @appdaemon.utils.sync_wrapper
    @hass_check
    @backoff.on_predicate(backoff.expo, max_time=10, on_giveup=on_giveup)
    async def set_light(self, entity_id: str, setting: LightSetting) -> bool:
        if setting == await self._get_light_setting(entity_id):
            return True

        if setting.brightness == 0:
            await self.turn_off(entity_id=entity_id)
        else:
            await self.turn_on(
                entity_id=entity_id,
                brightness=setting.brightness,
                color_temp=setting.color_temperature,
            )
        return False

    @appdaemon.utils.sync_wrapper
    @hass_check
    async def _get_light_setting(self, entity_id: str) -> LightSetting:
        base_state = await self.get_state(entity_id)
        if base_state == "off":
            return LightSetting.OFF
        assert base_state == "on"

        return LightSetting(
            brightness=await self.get_state(entity_id, attribute="brightness"),
            color_temperature=await self.get_state(entity_id, attribute="color_temp"),
        )
