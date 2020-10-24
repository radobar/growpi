# Specifies the type of sensor reading
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class SensorType(Enum):
    PIN = 0
    HOURS = 1
    MINUTES = 2


# Sensor metadata used to identify sensor from which to read input
@dataclass
class Sensor:
    type: SensorType
    value_name: str
    pin: int

    def __post_init__(self):
        self.type = SensorType(self.type)

