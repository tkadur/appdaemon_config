from __future__ import annotations

from dataclasses import dataclass, field
from enum import auto, unique
import re
from typing import ClassVar, Optional

from appdaemon.plugins.hass.hassapi import Hass

from curve import calculate_light_setting
from light_setting import LightSetting
from switch import (
    HueDimmerSwitch,
    bathroom_dimmer_switch,
    bedroom_dimmer_switch,
    living_room_dimmer_switch,
)
from util import StrEnum, irange


@dataclass(frozen=True)
class Light:
    entity_id: str

    def set(self, hass: Hass, setting: LightSetting, skip_fade: bool) -> None:
        if skip_fade:
            transition = 1
        else:
            transition = 10

        if setting.brightness == 0:
            hass.turn_off(self.entity_id, transition=transition)
        else:
            hass.turn_on(
                self.entity_id,
                brightness_pct=setting.brightness,
                kelvin=setting.color_temperature,
                transition=transition,
            )


@dataclass(frozen=True)
class Fixture:
    lights: list[Light]

    def set(self, hass: Hass, setting: LightSetting, skip_fade: bool = False) -> None:
        # For very low settings, since lights can't go lower than 1% we can
        # try to emulate lower brightnesses by turning on a subset of the lights to 1%.
        # To make transitions across the boundary smoother we also re-scale
        # brightnesses above the boundary.

        BOUNDARY = 6

        lights_to_set = self.lights
        if setting.brightness > BOUNDARY:
            setting = setting.with_brightness(
                int(((setting.brightness - BOUNDARY) / (100 - BOUNDARY)) * 100)
            )
        elif setting.brightness > 0:
            num_lights_to_set = max(
                1, int(round((setting.brightness * len(self.lights)) / BOUNDARY))
            )
            lights_to_set = self.lights[:num_lights_to_set]

            setting = setting.with_brightness(1)

            # Turn off unneeded lights
            for light in self.lights[num_lights_to_set:]:
                light.set(hass, LightSetting.OFF, skip_fade)

        for light in lights_to_set:
            light.set(hass, setting, skip_fade)


@dataclass(frozen=True)
class Room:
    switch: HueDimmerSwitch
    fixtures: list[Fixture]

    def refresh(self, hass: Hass) -> None:
        setting = calculate_light_setting(hass.time())
        skip_fade = False

        switch_state = self.switch.get_state(hass)
        if switch_state == HueDimmerSwitch.State.OFF:
            setting = setting.with_brightness(0)
            skip_fade = True
        elif switch_state == HueDimmerSwitch.State.ON:
            setting = setting.with_brightness(100)
            skip_fade = True

        for fixture in self.fixtures:
            fixture.set(hass, setting, skip_fade)


@dataclass(frozen=True)
class Home:
    rooms: list[Room]

    def refresh(self, hass: Hass) -> None:
        for room in self.rooms:
            room.refresh(hass)


# Light declarations

bathroom = Room(
    switch=bathroom_dimmer_switch,
    fixtures=[
        Fixture([Light("light.bathroom_hallway")]),
        Fixture([Light(f"light.bathroom_mirror_{bulb}") for bulb in irange(1, 4)]),
    ],
)

bedroom = Room(
    switch=bedroom_dimmer_switch,
    fixtures=[
        Fixture(
            [Light(f"light.bedroom_vidja_{fixture}_{bulb}") for bulb in irange(1, 6)]
        )
        for fixture in irange(1, 4)
    ],
)

dining_room = Room(
    switch=living_room_dimmer_switch,
    fixtures=[Fixture([Light("light.dining_room_fan")])],
)

hallway = Room(
    switch=living_room_dimmer_switch, fixtures=[Fixture([Light("light.hallway")])]
)

kitchen = Room(
    switch=living_room_dimmer_switch,
    fixtures=[Fixture([Light(f"light.kitchen_{bulb}") for bulb in irange(1, 2)])],
)

living_room = Room(
    switch=living_room_dimmer_switch,
    fixtures=[
        Fixture(
            [
                Light(f"light.living_room_vidja_{fixture}_{bulb}")
                for bulb in irange(1, 6)
            ]
        )
        for fixture in irange(1, 4)
    ],
)

toilet = Room(
    switch=bathroom_dimmer_switch,
    fixtures=[
        Fixture(
            [Light(f"light.toilet_{bulb}") for bulb in irange(1, 2)],
        ),
    ],
)

all_rooms = [bathroom, bedroom, dining_room, hallway, kitchen, living_room, toilet]

home = Home(
    all_rooms
)
