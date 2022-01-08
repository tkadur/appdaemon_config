from __future__ import annotations

from typing import Any

from base_app import BaseApp
from hue_event import Event as HueEvent
from lights import home
from switch import HueDimmerSwitch


class ProcessSwitchEvents(BaseApp):
    async def initialize(self) -> None:
        self.listen_event(self.hue_event, "hue_event")

    async def hue_event(
        self, event_name: str, data: dict[str, Any], kwargs: dict[str, Any]
    ) -> None:
        try:
            switch_event = HueDimmerSwitch.Event.from_hue_event(
                HueEvent.parse_obj(data)
            )
            switch = switch_event.switch
            sensor = switch.sensor

            old_state = await sensor.get_state(self)

            if (
                await switch.process_event(self, switch_event)
                == HueDimmerSwitch.ProcessResult.IGNORED
            ):
                return

            new_state = await sensor.get_state(self)
            self.log(
                f"Switch sensor {sensor.entity_name} changed from state {old_state} to state {new_state}."
            )
        except:
            self.notify_exception()
            raise
