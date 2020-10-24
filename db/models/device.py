import collections
from dataclasses import dataclass
from typing import NamedTuple

import typing

from db.models.sensor import Sensor


# Condition under which a device is turned on
@dataclass
class TurnOnCondition:
    min_val: float
    max_val: float
    sensor: Sensor

    def __post_init__(self):
        if isinstance(self.sensor, collections.Mapping):
            self.sensor = Sensor(**self.sensor)


# Device that can be turned on using a GPIO pin
@dataclass
class Device:
    id: str
    pin: int
    state: bool
    turn_on_conditions: typing.List[TurnOnCondition]
    override: typing.Union[bool, None]

    def __post_init__(self):
        self.turn_on_conditions = [
                TurnOnCondition(**condition) if isinstance(condition, collections.Mapping) else condition for condition in self.turn_on_conditions
        ]
