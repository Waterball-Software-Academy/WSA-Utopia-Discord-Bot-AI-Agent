from typing import Optional

from fastapi import Depends
from pymongo.database import Database

from commons.errors import NotFoundException
from commons.mongo.pymongo_get_database import MongoDatabaseDependency
from commons.utils.logging import get_logger
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus

logger = get_logger("speech_repo", diagnose=True)


class SpeechApplicationRepository:
    def __init__(self, db: Database):
        self.applications = db['SpeechApplication']

    def save(self, application: SpeechApplication) -> SpeechApplication:
        result = self.applications.update_one(
            {"_id": application._id},
            {"$set": application.to_dict()}, upsert=True)

        logger.info(
            f'[Saved SpeechApplication] '
            f'{{"upserted_id":"{result.upserted_id}", "modified":"{result.modified_count}"}}')
        return application

    def update_speech_application_review_status(self, speech_id: str,
                                                new_status: ApplicationReviewStatus,
                                                deny_reason: Optional[str] = None):
        result = self.applications.update_one(
            {"_id": speech_id},
            {"$set": {"application_review_status": str(new_status), "deny_reason": deny_reason}},
        )

        if result.modified_count == 0:
            raise NotFoundException("Speech Application", speech_id)

        logger.info(
            f'[Updated SpeechApplication] '
            f'{{"upserted_id":"{result.upserted_id}", '
            f'"modified":"{result.modified_count}", "new_status":"{new_status.name}"}}')

    def find_by_id(self, speech_id: str) -> Optional[SpeechApplication]:
        speech_application = SpeechApplication.from_dict(self.applications.find_one({"_id": speech_id}))
        speech_application._id = str(speech_application._id)  # Set _id to prevent json serialization issues
        return speech_application


def init_speech_application_repository(db=MongoDatabaseDependency):
    return SpeechApplicationRepository(db)


Dependency = Depends(init_speech_application_repository)
