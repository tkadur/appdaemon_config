from __future__ import annotations

from typing import Any

from base_app import BaseApp
from hue_event import Event as HueEvent
from switch import HueDimmerSwitch, bedroom_dimmer_switch


class ProcessSwitchEvents(BaseApp):
    def initialize(self) -> None:
        self.listen_event(self.hue_event, "hue_event")

    def hue_event(
        self, event_name: str, data: dict[str, Any], kwargs: dict[str, Any]
    ) -> None:
        try:
            hue_event = HueEvent.parse_obj(data)
            switch_event = HueDimmerSwitch.Event.from_hue_event(hue_event)

            switch = switch_event.switch
            old_state = switch.get_state(self)

            process_result = switch_event.process(self)
            if process_result == HueDimmerSwitch.Event.ProcessResult.PROCESSED:
                self.log(
                    f"Switch {switch} changed from state {old_state} to state {switch.get_state(self)}."
                )
            else:
                self.log(f"Ignored {switch_event}")
        except:
            self.notify_exception()
            raise
