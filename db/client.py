import datetime
import typing

import google
from google.cloud.firestore_v1 import CollectionReference, DocumentReference

from db.models.device import Device, TurnOnCondition


class DbClient(object):
    SENSOR_DATA_COLLECTION = u'sensors'
    SETTINGS_COLLECTION = u'settings'

    def __init__(self, db_client: google.cloud.firestore_v1.client.Client):
        """DbClient implements methods used to perform db operations

        :type db_client: client used to perform operations over the database
        """
        self.client = db_client

    def read_settings(self) -> typing.List[Device]:
        devices = []
        settings_col: CollectionReference = self.client.collection(self.SETTINGS_COLLECTION)
        docs = settings_col.stream()
        for doc in docs:
            doc_dict: dict = doc.to_dict()
            # devices.append(
            #     Device(id=doc_dict['id'], turn_on_conditions=conditions, pin=doc_dict['pin'],
            #            override=doc_dict['override']))
            devices.append(
                Device(override=None, **doc_dict)
            )
        return devices

    def put_sensor_data(self, time_of_reading: datetime.datetime, temperature: float, humidity: float):
        doc_ref = self.client.collection(self.SENSOR_DATA_COLLECTION).document()
        doc_ref.set({
            u'createdAt': time_of_reading,
            u'temperature': temperature,
            u'humidity': humidity
        })

    def put_device_state(self, device):
        doc_ref: DocumentReference = self.client.collection(self.SETTINGS_COLLECTION).document(device.id)
        doc_ref.update({'state': device.state})

