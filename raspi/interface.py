import datetime
import time

import Adafruit_DHT
import typing

from Adafruit_DHT.common import get_platform

from db.models.device import TurnOnCondition, Device
from db.models.sensor import SensorType


class RaspiInterface(object):
    DELAY_SECONDS = 2
    RETRIES = 15

    # TODO make generic
    def __init__(self, sensor_client: Adafruit_DHT.common, sensor_model: int, gpio: int):
        self.gpio = gpio
        self.sensor_model = sensor_model
        self.sensor_client = sensor_client
        self.pins_data_dict = {}

    @staticmethod
    def __compare_settings_to_reading(min_val, max_val, reading):
        # Decide if you want this Noneable
        if min_val is None or max_val is None:
            return True
        return (
                min_val < reading or reading < max_val
        ) if max_val < min_val else (
                min_val < reading < max_val
        )

    def check_conditions(self, turn_on_conditions: typing.List[TurnOnCondition]):
        now = datetime.datetime.now()
        for condition in turn_on_conditions:
            if condition.sensor.type == SensorType.MINUTES:
                if not self.__compare_settings_to_reading(condition.min_val, condition.max_val, now.minute):
                    return False
            elif condition.sensor.type == SensorType.HOURS:
                if not self.__compare_settings_to_reading(condition.min_val, condition.max_val, now.hour):
                    return False
            else:
                if not self.__compare_settings_to_reading(condition.min_val, condition.max_val,
                                                          self.pins_data_dict[condition.sensor.pin][
                                                              condition.sensor.value_name]):
                    return False
        return True

    def apply_settings(self, device: Device):
        device.state = device.override if device.override is not None else self.check_conditions(
            device.turn_on_conditions
        )
        # TODO add device.pin output, that's why there's no ternary
        return device.state

    def get_sensor_data(self) -> typing.Tuple[float, float]:
        for i in range(self.RETRIES):
            try:
                humidity, temperature = self.sensor_client.read(self.sensor_model, self.gpio)
            except RuntimeError as e:
                humidity, temperature = 0.0, 0.0
            print("Read attempt: hum{} temp{}".format(humidity, temperature))
            if humidity is not None and temperature is not None:
                self.pins_data_dict[self.gpio] = {'humidity': humidity, 'temperature': temperature}
                return humidity, temperature
            time.sleep(self.DELAY_SECONDS)
        return 0.0, 0.0
