import datetime
import time
from enum import Enum
from typing import Tuple, NamedTuple

import firebase_admin
import google
import typing
from Adafruit_DHT.common import get_platform
from firebase_admin import credentials
from firebase_admin import firestore

from config import settings
import Adafruit_DHT

SENSOR_DATA_COLLECTION = u'sensors'
SETTINGS_COLLECTION = u'settings'


class DeviceSettings(NamedTuple):
    working: bool
    start_time: str
    end_time: str
    max_temp: float
    min_temp: float
    max_humidity: float
    min_humidity: float
    max_ph: float
    min_ph: float


class SensorType(Enum):
    PIN = 0
    HOURS = 1
    MINUTES = 2


class Sensor(NamedTuple):
    name: str
    type: Enum
    pinId: typing.Union[str, None]


class DbClient(object):
    def __init__(self, db_client: google.cloud.firestore_v1.client.Client):
        self.client = db_client

    def read_settings(self, device_id) -> DeviceSettings:
        doc_ref = self.client.collection(SETTINGS_COLLECTION).document(device_id)
        doc = doc_ref.get()
        if doc.exists:
            try:
                return DeviceSettings(**doc)
            except TypeError() as e:
                print("Invalid settings format: {}".format(e))

        raise Exception("FUCK")

    def put_sensor_data(self, time_of_reading: datetime.datetime, temperature: float, humidity: float):
        doc_ref = self.client.collection(SENSOR_DATA_COLLECTION).document()
        doc_ref.set({
            u'createdAt': time_of_reading,
            u'temperature': temperature,
            u'humidity': humidity
        })


class RaspiInterface(object):
    DELAY_SECONDS = 2
    RETRIES = 15

    # TODO make generic
    def __init__(self, sensor_client: Adafruit_DHT.common, sensor_model: int, gpio: int):
        self.gpio = gpio
        self.sensor_model = sensor_model
        self.sensor_client = sensor_client
        self.platform = get_platform()

    # def apply_settings(self, settings: GrowBoxSettings):
    #     pass

    def get_sensor_data(self) -> Tuple[float, float]:
        for i in range(self.RETRIES):
            humidity, temperature = raspi.sensor_client.read(self.sensor_model, self.gpio, self.platform)
            print("Read attempt: hum{} temp{}".format(humidity,temperature))
            if humidity is not None and temperature is not None:
                return humidity, temperature
            time.sleep(self.DELAY_SECONDS)
        return 0.0, 0.0


#
#
# class TemperatureTuple(NamedTuple):
#
#
# class Device(NamedTuple):
#     start_time: str
#     end_time: str
#     working: bool
#     max_temp: float
#     min_temp: float
#     max_humidity: float
#     min_humidity: float
#     max_ph: float
#     min_ph: float
#     on_period: str
#     off_period: str
#     time_triple:
#
#
#
# class Pin(dict):
#     damn: int = 5
#
#     def set_state(state: bool):
#         pass
#
#     @staticmethod
#     def __compare_settings_to_reading(min_val, max_val, reading):
#         if min_val is None or max_val is None:
#             return True
#         return (
#                 min_val < reading or reading < max_val
#         ) if max_val < min_val else (
#                 min_val < reading < max_val
#         )
#
#     def parse_settings(self, settings: Device):
#         time_bit = self.__compare_settings_to_reading(settings['start_hour'], settings['end_hour'],
#                                                       datetime.datetime.now().hour)
#         wet_bit =  self.__compare_settings_to_reading(settings['min_temp'], settings['max_temp'],
#                                                       datetime.datetime.now().hour)
#         temp_bit = self.__compare_settings_to_reading(settings['min_temp'], settings['max_temp'],
#                                                       datetime.datetime.now().hour)

if __name__ == '__main__':
    cred = credentials.ApplicationDefault()
    project_id = settings.project_id
    sensor_gpio = settings.gpio
    sensor_model = settings.sensor_model
    # Use the application default credentials
    firebase_admin.initialize_app(cred, {
        'projectId': project_id,
    })
    sensor_client = Adafruit_DHT.common
    db = firestore.client()
    client = DbClient(db)
    raspi = RaspiInterface(sensor_client, sensor_model, sensor_gpio)
    print(settings)
    print(sensor_gpio)
    while True:
        # growbox_settings = client.read_settings()
        # raspi.apply_settings(growbox_settings)
        humidity, temp = raspi.get_sensor_data()
        client.put_sensor_data(datetime.datetime.now(), temp, humidity)
        time.sleep(60)
