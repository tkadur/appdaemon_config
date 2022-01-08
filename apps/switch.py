from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto, unique
from functools import cached_property
from types import MappingProxyType
from typing import Any, ClassVar, Generic, Mapping, Optional, Protocol, Type, TypeVar

from appdaemon.plugins.hass.hassapi import Hass

from hue_event import Event as HueEvent
from light_setting import LightSetting
from util import StrEnum


@dataclass(frozen=True)
class HueDimmerSwitch:
    """
    Represents a physical Hue dimmer switch
    """

    id: str
    sensor: SwitchSensor[HueDimmerSwitch.State]

    @unique
    class Button(IntEnum):
        POWER = 1
        BRIGHTNESS_UP = 2
        BRIGHTNESS_DOWN = 3
        HUE = 4

    @unique
    class ButtonAction(StrEnum):
        # Down events are not guaranteed to be sent
        INITIAL_PRESS = auto()

        # Up and hold events are guaranteed to be sent
        SHORT_RELEASE = auto()
        LONG_RELEASE = auto()
        REPEAT = auto()

    @dataclass(frozen=True)
    class Event:
        switch: HueDimmerSwitch
        button: HueDimmerSwitch.Button
        action: HueDimmerSwitch.ButtonAction

        @staticmethod
        def from_hue_event(hue_event: HueEvent) -> HueDimmerSwitch.Event:
            button = HueDimmerSwitch.Button(hue_event.subtype)
            action = HueDimmerSwitch.ButtonAction(hue_event.type.upper())

            return HueDimmerSwitch.Event(
                switch=SWITCHES_BY_ID[hue_event.id.removesuffix("_button")],
                button=button,
                action=action,
            )

    @unique
    class ProcessResult(Enum):
        PROCESSED = auto()
        IGNORED = auto()

    def process_event(self, app: Hass, event: HueDimmerSwitch.Event) -> ProcessResult:
        if event.switch != self:
            raise ValueError(
                f"Event was sent to the wrong switch. \n"
                f"Switch: {self} \n"
                f"Event: {event}"
            )

        # We ignore down actions because they're unreliable
        if event.action == HueDimmerSwitch.ButtonAction.INITIAL_PRESS:
            return self.ProcessResult.IGNORED

        if event.button == HueDimmerSwitch.Button.POWER:
            new_state = HueDimmerSwitch.State.OFF
        elif event.button == HueDimmerSwitch.Button.BRIGHTNESS_UP:
            new_state = HueDimmerSwitch.State.ON
        elif (
            event.button == HueDimmerSwitch.Button.BRIGHTNESS_DOWN
            and event.action == HueDimmerSwitch.ButtonAction.SHORT_RELEASE
        ):
            new_state = HueDimmerSwitch.State.HALF_ON
        elif (
            event.button == HueDimmerSwitch.Button.BRIGHTNESS_DOWN
            and event.action == HueDimmerSwitch.ButtonAction.LONG_RELEASE
        ):
            new_state = HueDimmerSwitch.State.QUARTER_ON
        elif event.button == HueDimmerSwitch.Button.HUE:
            new_state = HueDimmerSwitch.State.DEFAULT
        else:
            return self.ProcessResult.IGNORED

        self.sensor.set_state(app, new_state)
        return self.ProcessResult.PROCESSED

    @unique
    class State(StrEnum):
        DEFAULT = auto()
        OFF = auto()
        QUARTER_ON = auto()
        HALF_ON = auto()
        ON = auto()

        def to_brightness(self) -> int:
            return {
                HueDimmerSwitch.State.OFF: 0,
                HueDimmerSwitch.State.QUARTER_ON: 10,
                HueDimmerSwitch.State.HALF_ON: 25,
                HueDimmerSwitch.State.ON: 100,
            }[self]


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

    def get_state(self, app: Hass, fall_back_to_default: bool = True) -> _State:
        raw_state = app.get_state(self.entity_id)

        try:
            return self.default_state.__class__(raw_state)
        except:
            if fall_back_to_default:
                self.set_state(app, self.default_state)
                return self.get_state(app, fall_back_to_default=False)
            else:
                raise

    def set_state(self, app: Hass, state: _State) -> None:
        app.set_state(self.entity_id, state=state)


# Sensor and switch declarations

toilet_dimmer_switch = HueDimmerSwitch(
    id="toilet_dimmer_switch",
    sensor=SwitchSensor(
        entity_name="toilet",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

bedroom_dimmer_switch = HueDimmerSwitch(
    id="bedroom_dimmer_switch",
    sensor=SwitchSensor(
        entity_name="bedroom",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

living_room_dimmer_switch = HueDimmerSwitch(
    id="living_room_dimmer_switch",
    sensor=SwitchSensor(
        entity_name="living_room",
        default_state=HueDimmerSwitch.State.DEFAULT,
    ),
)

ALL_SWITCHES = (
    toilet_dimmer_switch,
    bedroom_dimmer_switch,
    living_room_dimmer_switch,
)

SWITCHES_BY_ID = MappingProxyType({switch.id: switch for switch in ALL_SWITCHES})
