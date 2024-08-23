from datetime import datetime
from enum import Enum
from typing import Optional, Any

from bson import ObjectId


class ApplicationReviewStatus(Enum):
    PENDING = 1
    ACCEPTED = 2
    DENIED = 3


class SpeechApplication:
    def __init__(self, _id: str,
                 title: str,
                 description: str,
                 speaker_name: str,
                 event_start_time: datetime,
                 event_end_time: datetime,
                 duration_in_mins: int,
                 cal_booking_id: int,
                 cal_booking_uid: str,
                 speaker_discord_id: str,
                 speaker_attendee_email: str,
                 application_review_status=ApplicationReviewStatus.PENDING,
                 apply_time=datetime.now(),
                 # Fields after accepted or denied
                 deny_reason: Optional[str] = None,
                 discord_event_id: Optional[str] = None,
                 google_calendar_official_event_id: Optional[str] = None):
        self._id = str(_id)
        self.title = title
        self.description = description
        self.speaker_name = speaker_name
        self.event_start_time = event_start_time
        self.event_end_time = event_end_time
        self.duration_in_mins = duration_in_mins
        self.cal_booking_id = cal_booking_id
        self.cal_booking_uid = cal_booking_uid
        self.speaker_discord_id = speaker_discord_id
        self.speaker_attendee_email = speaker_attendee_email
        self.application_review_status = application_review_status
        self.apply_time = apply_time
        self.deny_reason = deny_reason
        self.discord_event_id = discord_event_id
        self.google_calendar_official_event_id = google_calendar_official_event_id

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "title": self.title,
            "description": self.description,
            "speaker_name": self.speaker_name,
            "event_start_time": self.event_start_time.isoformat() if self.event_start_time else None,
            "event_end_time": self.event_end_time.isoformat() if self.event_end_time else None,
            "duration_in_mins": self.duration_in_mins,
            "cal_booking_id": self.cal_booking_id,
            "cal_booking_uid": self.cal_booking_uid,
            "speaker_discord_id": self.speaker_discord_id,
            "speaker_attendee_email": self.speaker_attendee_email,
            "application_review_status": self.application_review_status.name,
            "apply_time": self.apply_time.isoformat() if self.apply_time else None,
            "deny_reason": self.deny_reason,
            "discord_event_id": self.discord_event_id,
            "google_calendar_official_event_id": self.google_calendar_official_event_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data["_id"],
            title=data["title"],
            description=data["description"],
            speaker_name=data["speaker_name"],
            event_start_time=datetime.fromisoformat(data["event_start_time"]) if data.get("event_start_time") else None,
            event_end_time=datetime.fromisoformat(data["event_end_time"]) if data.get("event_end_time") else None,
            duration_in_mins=data["duration_in_mins"],
            cal_booking_id=data["cal_booking_id"],
            cal_booking_uid=data["cal_booking_uid"],
            speaker_discord_id=data["speaker_discord_id"],
            speaker_attendee_email=data["speaker_attendee_email"],
            application_review_status=ApplicationReviewStatus[data["application_review_status"]] if data.get(
                "application_review_status") else ApplicationReviewStatus.PENDING,
            apply_time=datetime.fromisoformat(data["apply_time"]) if data.get("apply_time") else datetime.now(),
            deny_reason=data.get("deny_reason"),
            discord_event_id=data.get("discord_event_id"),
            google_calendar_official_event_id=data.get("google_calendar_official_event_id"),
        )

    @property
    def id(self) -> str:
        return self._id
