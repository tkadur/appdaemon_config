from __future__ import annotations

from dataclasses import dataclass, field
from enum import auto, unique
from functools import cached_property
import re
from typing import ClassVar, Optional

from base_app import BaseApp
from curve import current_curve_setting
from light_setting import LightSetting
from switch import (
    HueDimmerSwitch,
    SwitchSensor,
    toilet_dimmer_switch,
    bedroom_dimmer_switch,
    living_room_dimmer_switch,
)
from util import irange

# Brightnesses below this value (inclusive) get special handling at the fixture level
LOW_BRIGHTNESS_BOUNDARY = 6


def is_low_brightness(brightness: int) -> bool:
    return 0 < brightness and brightness <= LOW_BRIGHTNESS_BOUNDARY


def rescale_normal_brightness(brightness: int) -> int:
    """
    Rescales brightnesses above the boundary to make transitions across
    the boundary smoother
    """
    assert not is_low_brightness(
        brightness
    ), f"Brightness {brightness} is below the low brightness boundary {LOW_BRIGHTNESS_BOUNDARY} and therefore should not be rescaled."

    if brightness == 0:
        return 0

    return int(
        ((brightness - LOW_BRIGHTNESS_BOUNDARY) / (100 - LOW_BRIGHTNESS_BOUNDARY)) * 100
    )


@dataclass(frozen=True)
class Light:
    entity_id: str

    def set(self, app: BaseApp, setting: LightSetting) -> None:
        app.set_light(self.entity_id, setting)


@dataclass(frozen=True)
class Fixture:
    lights: list[Light]

    def set(self, app: BaseApp, setting: LightSetting) -> None:
        # For very low settings, since lights can't go lower than 1% we can
        # try to emulate lower brightnesses by turning on a subset of the lights to 1%.
        # To make transitions across the boundary smoother we also re-scale
        # brightnesses above the boundary.

        if is_low_brightness(setting.brightness):
            num_lights_to_set = max(
                1,
                int(
                    round(
                        (setting.brightness * len(self.lights))
                        / LOW_BRIGHTNESS_BOUNDARY
                    )
                ),
            )
            lights_to_set = self.lights[:num_lights_to_set]

            setting = setting.with_brightness(1)

            # Turn off unneeded lights
            for light in self.lights[num_lights_to_set:]:
                light.set(app, LightSetting.OFF)
        else:
            lights_to_set = self.lights

        for light in lights_to_set:
            light.set(app, setting)


@dataclass(frozen=True)
class Room:
    entity_id: str
    switch_sensor: SwitchSensor[HueDimmerSwitch.State]
    fixtures: list[Fixture]
    minimum_brightness: Optional[int] = None

    @cached_property
    def readable_name(self) -> str:
        _, name = self.entity_id.split(".")
        return name.replace("_", " ").title()

    def current_setting(self, app: BaseApp) -> LightSetting:
        switch_state = self.switch_sensor.get_state(app)
        setting = current_curve_setting(app)
        if switch_state != HueDimmerSwitch.State.DEFAULT:
            setting = setting.with_brightness(switch_state.to_brightness())

        if self.minimum_brightness is not None:
            setting = setting.with_brightness(
                max(setting.brightness, self.minimum_brightness)
            )

        return setting

    def refresh(self, app: BaseApp) -> None:
        setting = self.current_setting(app)

        # For low brightnesses, we need to manually iterate over every fixture
        # to do the partial fixture illumination stuff
        if is_low_brightness(setting.brightness):
            for fixture in self.fixtures:
                fixture.set(app, setting)
        # For normal brightnesses, we can directly set every fixture at once
        else:
            setting = setting.with_brightness(
                rescale_normal_brightness(setting.brightness)
            )
            app.set_light(self.entity_id, setting)


@dataclass(frozen=True)
class Home:
    rooms: list[Room]

    def refresh(self, app: BaseApp) -> None:
        for room in self.rooms:
            room.refresh(app)


# Light declarations

bathroom = Room(
    entity_id="light.bathroom",
    switch_sensor=toilet_dimmer_switch.sensor,
    fixtures=[
        Fixture([Light("light.bathroom_hallway")]),
        Fixture([Light(f"light.bathroom_mirror_{bulb}") for bulb in irange(1, 4)]),
    ],
)

bedroom = Room(
    entity_id="light.bedroom",
    switch_sensor=bedroom_dimmer_switch.sensor,
    fixtures=[
        Fixture(
            [Light(f"light.bedroom_vidja_{fixture}_{bulb}") for bulb in irange(1, 6)]
        )
        for fixture in irange(1, 4)
    ],
)

dining_room = Room(
    entity_id="light.dining_room",
    switch_sensor=living_room_dimmer_switch.sensor,
    fixtures=[Fixture([Light("light.dining_room_fan")])],
)

hallway = Room(
    entity_id="light.hallway",
    switch_sensor=living_room_dimmer_switch.sensor,
    fixtures=[Fixture([Light("light.hallway")])],
)

kitchen = Room(
    entity_id="light.kitchen",
    switch_sensor=living_room_dimmer_switch.sensor,
    fixtures=[Fixture([Light(f"light.kitchen_{bulb}") for bulb in irange(1, 2)])],
)

living_room = Room(
    entity_id="light.living_room",
    switch_sensor=living_room_dimmer_switch.sensor,
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
    entity_id="light.toilet",
    switch_sensor=toilet_dimmer_switch.sensor,
    fixtures=[
        Fixture(
            [Light(f"light.toilet_{bulb}") for bulb in irange(1, 2)],
        ),
    ],
)

home = Home(
    rooms=[bathroom, bedroom, dining_room, hallway, kitchen, living_room, toilet],
)
