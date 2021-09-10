from __future__ import annotations

from typing import Any

from base_app import BaseApp
from hue_event import Event as HueEvent
from control import all_rooms
from switch import HueDimmerSwitch


class ProcessSwitchEvents(BaseApp):
    def initialize(self) -> None:
        self.listen_event(self.hue_event, "hue_event")

    def hue_event(
        self, event_name: str, data: dict[str, Any], kwargs: dict[str, Any]
    ) -> None:
        try:
            switch_event = HueDimmerSwitch.Event.from_hue_event(HueEvent.parse_obj(data))

            if switch_event.process(self) == HueDimmerSwitch.Event.ProcessResult.IGNORED:
                self.log(f"Ignored {switch_event}")
                return

            switch = switch_event.switch
            old_state = switch.get_state(self)

            self.log(
                f"Switch {switch} changed from state {old_state} to state {switch.get_state(self)}."
            )

            for room in all_rooms:
                if switch == room.switch:
                    room.refresh()
        except:
            self.notify_exception()
            raise
