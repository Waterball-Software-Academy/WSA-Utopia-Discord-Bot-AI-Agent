from typing import Optional, Mapping, Iterable

from fastapi import Depends
from pymongo.database import Database

from commons.errors import NotFoundException
from commons.mongo.pymongo_get_database import MongoDatabaseDependency, get_mongo_database_instance
from commons.utils.logging import get_logger
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus

logger = get_logger("speech_repo", diagnose=True)


class SpeechApplicationRepository:
    def __init__(self, db: Database):
        self.applications = db['SpeechApplication']

    def save(self, application: SpeechApplication) -> SpeechApplication:
        result = self.applications.update_one(
            {"_id": application.id},
            {"$set": application.to_dict()}, upsert=True)

        logger.info(
            f'[Saved SpeechApplication] {{"id":"{application.id}"}}')
        return application

    def update_speech_application_review_status(self, speech_id: str,
                                                new_status: ApplicationReviewStatus,
                                                deny_reason: Optional[str] = None):
        self.update_speech_application(speech_id, {"application_review_status": new_status.name,
                                                   "deny_reason": deny_reason})

    def update_speech_application(self, speech_id: str,
                                  update_dict: dict[str, str | int | None]):
        result = self.applications.update_one(
            {"_id": speech_id},
            {"$set": update_dict},
        )

        if result.modified_count == 0:
            raise NotFoundException("Speech Application", speech_id)

        logger.debug(
            f'[Updated SpeechApplication] '
            f'{{"matched_count":"{result.matched_count}", "modified":"{result.modified_count}", ' +
            ', '.join([f'"{key}":"{value}"' if isinstance(value, str)
                       else f'"{key}":{value}' for key, value in update_dict.items()]) + '}}')

    def find_by_id(self, speech_id: str) -> Optional[SpeechApplication]:
        data = self.applications.find_one({"_id": speech_id})  # type: Mapping
        if data is None:
            return None
        return SpeechApplication.from_dict({**data,
                                            # Convert the ObjectId(_id) to string to prevent json serialization issues
                                            "_id": str(data["_id"])})

    def delete_by_id(self, speech_id: str):
        self.applications.delete_one({"_id": speech_id})
        logger.debug(f'[Deleted Speech Application from DB] {{"id":"{speech_id}"}}')


def init_speech_application_repository(db=MongoDatabaseDependency):
    return SpeechApplicationRepository(db)


Dependency = Depends(init_speech_application_repository)

if __name__ == '__main__':
    # Script for test
    db = get_mongo_database_instance()
    repo = SpeechApplicationRepository(db)

    repo.delete_by_id('2XTAXWu5hrU7KPZBpNo7F8')
