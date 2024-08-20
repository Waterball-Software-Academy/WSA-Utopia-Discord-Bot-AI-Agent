from pymongo.database import Database

from speech.app.entities.speech_application import SpeechApplication


class SpeechApplicationRepository:
    def __init__(self, db: Database):
        self.collection = db['speech_application']

    def save(self, speech_application: SpeechApplication):
        result = self.collection.insert_one(speech_application.to_dict())
        speech_application.form_id = str(result.inserted_id)

    def find_by_form_id(self, form_id: str) -> SpeechApplication | None:
        data = self.collection.find_one({"form_id": form_id})
        if data:
            return SpeechApplication.from_dict(dict(data))
        return None
