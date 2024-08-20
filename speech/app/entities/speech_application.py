from datetime import datetime
from enum import Enum
from typing import Optional, Any

from bson import ObjectId


class ApplicationReviewStatus(Enum):
    PENDING = 1
    ACCEPTED = 2
    DENIED = 3


class SpeechApplication:
    def __init__(self, title: str,
                 speaker_discord_id: str, speaker_name: str,
                 description: str,
                 event_start_time: datetime,
                 duration_in_mins: int,
                 _id: Optional[str] = None,
                 application_review_status=ApplicationReviewStatus.PENDING,
                 apply_time=datetime.now(),
                 deny_reason: Optional[str] = None):
        self._id = _id
        self.speaker_discord_id = speaker_discord_id
        self.speaker_name = speaker_name
        self.title = title
        self.description = description
        self.event_start_time = event_start_time
        self.duration_in_mins = duration_in_mins
        self.application_review_status = application_review_status
        self.deny_reason = deny_reason
        self.apply_time = apply_time

    def to_dict(self):
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "speaker_discord_id": self.speaker_discord_id,
            "speaker_name": self.speaker_name,
            "event_start_time": self.event_start_time.isoformat() if isinstance(self.event_start_time,
                                                                                datetime) else self.event_start_time,
            "duration_in_mins": self.duration_in_mins,
            "application_review_status": self.application_review_status.name,
            "deny_reason": self.deny_reason,
            "apply_time": self.apply_time.isoformat() if isinstance(self.apply_time, datetime) else self.apply_time
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            title=data.get("title"),
            speaker_discord_id=data.get("speaker_discord_id"),
            speaker_name=data.get("speaker_name"),
            description=data.get("description"),
            event_start_time=datetime.fromisoformat(data.get("event_start_time")) if data.get(
                "event_start_time") else None,
            duration_in_mins=data.get("duration_in_mins"),
            _id=data.get("_id"),
            application_review_status=data.get("application_review_status", ApplicationReviewStatus.PENDING),
            deny_reason=data.get("deny_reason"),
            apply_time=datetime.fromisoformat(data.get("apply_time")) if data.get("apply_time") else None
        )
