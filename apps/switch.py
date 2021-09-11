from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto, unique
from functools import cached_property
from types import MappingProxyType
from typing import Any, ClassVar, Generic, Mapping, Optional, Protocol, Type, TypeVar

from appdaemon.plugins.hass.hassapi import Hass

from curve import current_light_setting
from hue_event import Event as HueEvent
from util import StrEnum


@dataclass(frozen=True)
class HueDimmerSwitch:
    """
    Represents a physical Hue dimmer switch
    """

    id: str
    unique_id: str
    sensor: SwitchSensor[HueDimmerSwitch.State]

    _EVENT_CODE_TO_BUTTON_ACTION: ClassVar[Mapping[int, tuple[Button, ButtonAction]]]

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

    @dataclass(frozen=True)
    class Event:
        switch: HueDimmerSwitch
        button: HueDimmerSwitch.Button
        action: HueDimmerSwitch.ButtonAction

        @staticmethod
        def from_hue_event(hue_event: HueEvent) -> HueDimmerSwitch.Event:
            button, action = HueDimmerSwitch._EVENT_CODE_TO_BUTTON_ACTION[
                hue_event.event
            ]
            return HueDimmerSwitch.Event(
                switch=SWITCHES_BY_ID[(hue_event.id, hue_event.unique_id)],
                button=button,
                action=action,
            )

    @unique
    class ProcessResult(Enum):
        PROCESSED = auto()
        IGNORED = auto()

    async def process_event(
        self, app: Hass, event: HueDimmerSwitch.Event
    ) -> ProcessResult:
        if event.switch != self:
            raise ValueError(
                f"Event was sent to the wrong switch. \n"
                f"Switch: {self} \n"
                f"Event: {event}"
            )

        # We ignore down actions because they're unreliable
        if event.action in (
            HueDimmerSwitch.ButtonAction.PRESS_DOWN,
            HueDimmerSwitch.ButtonAction.HOLD_DOWN,
        ):
            return self.ProcessResult.IGNORED

        new_state = {
            HueDimmerSwitch.Button.POWER: HueDimmerSwitch.State.OFF,
            HueDimmerSwitch.Button.BRIGHTNESS_UP: HueDimmerSwitch.State.ON,
            HueDimmerSwitch.Button.BRIGHTNESS_DOWN: HueDimmerSwitch.State.HALF_ON,
            HueDimmerSwitch.Button.HUE: HueDimmerSwitch.State.DEFAULT,
        }[event.button]

        await self.sensor.set_state(app, new_state)
        return self.ProcessResult.PROCESSED

    @unique
    class State(StrEnum):
        DEFAULT = auto()
        OFF = auto()
        HALF_ON = auto()
        ON = auto()

        def to_brightness(self) -> int:
            return {
                HueDimmerSwitch.State.OFF: 0,
                HueDimmerSwitch.State.HALF_ON: 25,
                HueDimmerSwitch.State.ON: 100,
            }[self]


HueDimmerSwitch._EVENT_CODE_TO_BUTTON_ACTION = {
    (button * 1000) + action: (button, action)
    for button in HueDimmerSwitch.Button
    for action in HueDimmerSwitch.ButtonAction
}


_State = TypeVar("_State", bound=StrEnum)


@dataclass(frozen=True)
class SwitchSensor(Generic[_State]):
    """
    Represents a phantom sensor entity controlled by one more more switches
    """

    entity_name: str
    default_state: _State

    @cached_property
    def entity_id(self) -> str:
        return f"switch.{self.entity_name}"

    async def get_state(self, app: Hass, fall_back_to_default: bool = True) -> _State:
        raw_state = await app.get_state(self.entity_id)

        try:
            return self.default_state.__class__(raw_state)
        except:
            if fall_back_to_default:
                await self.set_state(app, self.default_state)
                return await self.get_state(app, fall_back_to_default=False)
            else:
                raise

    async def set_state(self, app: Hass, state: _State) -> None:
        await app.set_state(self.entity_id, state=state)


# Sensor and switch declarations

bathroom_dimmer_switch = HueDimmerSwitch(
    id="bathroom_dimmer_switch",
    unique_id="",
    sensor=SwitchSensor(
        entity_name="bathroom",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

bedroom_dimmer_switch = HueDimmerSwitch(
    id="bedroom_dimmer_switch",
    unique_id="00:17:88:01:09:a7:1b:9e-01-fc00",
    sensor=SwitchSensor(
        entity_name="bedroom",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

living_room_dimmer_switch = HueDimmerSwitch(
    id="living_room_dimmer_switch",
    unique_id="00:17:88:01:09:a7:44:61-01-fc00",
    sensor=SwitchSensor(
        entity_name="living_room",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

ALL_SWITCHES = (
    bathroom_dimmer_switch,
    bedroom_dimmer_switch,
    living_room_dimmer_switch,
)

SWITCHES_BY_ID = MappingProxyType(
    {(switch.id, switch.unique_id): switch for switch in ALL_SWITCHES}
)
