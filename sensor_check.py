import datetime
import time

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

from config import settings
import Adafruit_DHT

from db.client import DbClient
from raspi.interface import RaspiInterface

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
    while True:
        humidity, temp = raspi.get_sensor_data()
        client.put_sensor_data(datetime.datetime.now(), temp, humidity)
        growbox_settings = client.read_settings()
        for device in growbox_settings:
            raspi.apply_settings(device)
            client.put_device_state(device)
        # TODO configurable settings
        time.sleep(60)
