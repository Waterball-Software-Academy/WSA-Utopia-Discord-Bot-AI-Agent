from typing import Optional

from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database

from commons.errors import NotFoundException
from commons.mongo.pymongo_get_database import MongoDatabaseDependency
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus


class SpeechApplicationRepository:
    def __init__(self, db: Database):
        self.applications = db['SpeechApplication']

    def save(self, speech_application: SpeechApplication) -> SpeechApplication:
        if speech_application._id:
            self.applications.update_one(
                {"_id": speech_application._id}, {"$set": speech_application.to_dict()})
        else:
            speech_application._id = ObjectId()
            result = self.applications.insert_one(speech_application.to_dict())
            speech_application._id = str(result.inserted_id)  # Set the _id after insertion
        return speech_application

    def update_speech_application_review_status(self, speech_id: str,
                                                new_status: ApplicationReviewStatus,
                                                deny_reason: Optional[str] = None):
        result = self.applications.update_one(
            {"_id": ObjectId(speech_id)},
            {"$set": {"application_review_status": str(new_status), "deny_reason": deny_reason}},
        )

        if result.modified_count == 0:
            raise NotFoundException("Speech Application", speech_id)

    def find_by_id(self, speech_id: str) -> Optional[SpeechApplication]:
        speech_application = SpeechApplication.from_dict(self.applications.find_one({"_id": ObjectId(speech_id)}))
        speech_application._id = str(speech_application._id) # Set _id to prevent json serialization issues
        return speech_application


def init_speech_application_repository(db=MongoDatabaseDependency):
    return SpeechApplicationRepository(db)


Dependency = Depends(init_speech_application_repository)
