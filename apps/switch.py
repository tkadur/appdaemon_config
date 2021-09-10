from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto, unique
from functools import cached_property
from types import MappingProxyType
from typing import Any, ClassVar, Mapping, Type, TypeVar

from appdaemon.plugins.hass.hassapi import Hass

from hue_event import Event as HueEvent
from util import StrEnum


@dataclass(frozen=True)
class HueDimmerSwitch:
    id: str
    unique_id: str

    @unique
    class Button(IntEnum):
        POWER = 1
        BRIGHTNESS_UP = 2
        BRIGHTNESS_DOWN = 3
        HUE = 4

    @unique
    class ButtonAction(IntEnum):
        # Down events are not guaranteed to be sent
        PRESS_DOWN = 0
        HOLD_DOWN = 1

        # Up events are guaranteed to be sent
        PRESS_UP = 2
        HOLD_UP = 3

    _EVENT_CODE_TO_BUTTON_ACTION: ClassVar[Mapping[int, tuple[Button, ButtonAction]]]

    @dataclass(frozen=True)
    class Event:
        switch: HueDimmerSwitch
        button: HueDimmerSwitch.Button
        action: HueDimmerSwitch.ButtonAction

        _Self = TypeVar("_Self", bound="HueDimmerSwitch.Event")

        @classmethod
        def from_hue_event(cls: Type[_Self], hue_event: HueEvent) -> _Self:
            button, action = HueDimmerSwitch._EVENT_CODE_TO_BUTTON_ACTION[
                hue_event.event
            ]
            return cls(
                switch=HueDimmerSwitch(id=hue_event.id, unique_id=hue_event.unique_id),
                button=button,
                action=action,
            )

        @unique
        class ProcessResult(Enum):
            PROCESSED = auto()
            IGNORED = auto()

        def process(self, hass: Hass) -> ProcessResult:
            if self.switch not in all_switches:
                return self.ProcessResult.IGNORED

            if (
                self.button == HueDimmerSwitch.Button.POWER
                and self.action == HueDimmerSwitch.ButtonAction.PRESS_UP
            ):
                if self.switch.get_state(hass) == HueDimmerSwitch.State.OFF:
                    new_state = HueDimmerSwitch.State.DEFAULT
                else:
                    new_state = HueDimmerSwitch.State.OFF

                self.switch.set_state(hass, new_state)
                return self.ProcessResult.PROCESSED

            elif (
                self.button == HueDimmerSwitch.Button.BRIGHTNESS_UP
                and self.action == HueDimmerSwitch.ButtonAction.PRESS_UP
            ):
                if self.switch.get_state(hass) != HueDimmerSwitch.State.OFF:
                    self.switch.set_state(hass, HueDimmerSwitch.State.ON)
                    return self.ProcessResult.PROCESSED

            elif (
                self.button == HueDimmerSwitch.Button.BRIGHTNESS_DOWN
                and self.action == HueDimmerSwitch.ButtonAction.PRESS_UP
            ):
                if self.switch.get_state(hass) != HueDimmerSwitch.State.OFF:
                    self.switch.set_state(hass, HueDimmerSwitch.State.DEFAULT)
                    return self.ProcessResult.PROCESSED

            return self.ProcessResult.IGNORED

    @cached_property
    def _entity_name(self) -> str:
        return f"switch.{self.id}"

    @unique
    class State(StrEnum):
        DEFAULT = auto()
        OFF = auto()
        ON = auto()

    def get_state(self, hass: Hass) -> State:
        state = hass.get_state(self._entity_name)
        if state is None:
            self.set_state(hass, self.State.DEFAULT)
            return self.get_state(hass)

        return self.State(state)

    def set_state(self, hass: Hass, state: State) -> None:
        hass.set_state(self._entity_name, state=state)


HueDimmerSwitch._EVENT_CODE_TO_BUTTON_ACTION = {
    (button * 1000) + action: (button, action)
    for button in HueDimmerSwitch.Button
    for action in HueDimmerSwitch.ButtonAction
}


bathroom_dimmer_switch = HueDimmerSwitch(id="bathroom_dimmer_switch", unique_id="")

bedroom_dimmer_switch = HueDimmerSwitch(
    id="bedroom_dimmer_switch", unique_id="00:17:88:01:09:a7:1b:9e-01-fc00"
)

living_room_dimmer_switch = HueDimmerSwitch(
    id="living_room_dimmer_switch", unique_id="00:17:88:01:09:a7:44:61-01-fc00"
)

all_switches = [
    bathroom_dimmer_switch,
    bedroom_dimmer_switch,
    living_room_dimmer_switch,
]
