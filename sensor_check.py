import datetime
import time
from typing import Tuple

import firebase_admin
import google
from firebase_admin import credentials
from firebase_admin import firestore

from config import settings

SENSOR_DATA_COLLECTION = u'sensors'
SETTINGS_COLLECTION = u'settings'


class GrowBoxSettings(object):
    def __init__(self, document):
        data = document.to_dict()
        self.light = data['light']
        self.fan = data['fan']
        self.light_start = data['light_start']
        self.light_end = data['light_end']


class DbClient(object):
    def __init__(self, client: google.cloud.firestore_v1.client.Client):
        self.client = client

    def read_settings(self) -> GrowBoxSettings:
        doc_ref = self.client.collection(SETTINGS_COLLECTION).document('growbox1')
        doc = doc_ref.get()
        if doc.exists:
            return GrowBoxSettings(doc)
        raise Exception("FUCK")

    def put_sensor_data(self, time_of_reading: datetime.datetime, temperature: float, humidity: float):
        doc_ref = self.client.collection(SENSOR_DATA_COLLECTION).document()
        doc_ref.set({
            u'createdAt': time_of_reading,
            u'temperature': temperature,
            u'humidity': humidity
        })


class RaspiInterface(object):
    def apply_settings(self, settings: GrowBoxSettings):
        pass

    def get_sensor_data(self) -> Tuple[float, float]:
        return 26, 60


if __name__ == '__main__':
    cred = credentials.ApplicationDefault()
    project_id = settings.project_id
    # Use the application default credentials
    firebase_admin.initialize_app(cred, {
        'projectId': project_id,
    })
    db = firestore.client()
    client = DbClient(db)
    raspi = RaspiInterface()
    while (True):
        growbox_settings = client.read_settings()
        raspi.apply_settings(growbox_settings)
        temp, humidity = raspi.get_sensor_data()
        client.put_sensor_data(datetime.datetime.now(), temp, humidity)
        time.sleep(60)
