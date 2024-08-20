from fastapi import Depends
from pymongo import MongoClient
from pymongo.database import Database

from commons.mongo.pymongo_get_database import MongoDatabaseDependency
from speech.app.entities.speech_application import SpeechApplication


class SpeechApplicationRepository:
    def __init__(self, db: Database):
        self.collection = db['speech_application']

    def save(self, speech_application: SpeechApplication) -> SpeechApplication:
        result = self.collection.insert_one(speech_application.to_dict())
        speech_application.speech_id = str(result.inserted_id)
        return speech_application

    def find_by_form_id(self, form_id: str) -> SpeechApplication | None:
        data = self.collection.find_one({"form_id": form_id})
        if data:
            return SpeechApplication.from_dict(dict(data))
        return None


def init_speech_application_repository(db=MongoDatabaseDependency):
    return SpeechApplicationRepository(db)


Dependency = Depends(init_speech_application_repository)
