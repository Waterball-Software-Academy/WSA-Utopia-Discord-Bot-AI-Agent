from datetime import datetime

from bson import ObjectId


# TODO: unsure if it works with the mongodb orm
class SpeechApplication:
    def __init__(self, title: str, speaker_discord_id: str, speaker_nickname: str, event_time: datetime,
                 form_id: str = None):
        self.title = title
        self.speaker_discord_id = speaker_discord_id
        self.speaker_nickname = speaker_nickname
        self.event_time = event_time
        self.form_id = form_id if form_id else str(ObjectId())

    def to_dict(self):
        return {
            "title": self.title,
            "speaker_discord_id": self.speaker_discord_id,
            "speaker_nickname": self.speaker_nickname,
            "event_time": self.event_time,
            "form_id": self.form_id,
        }

    @staticmethod
    def from_dict(data: dict):
        return SpeechApplication(
            title=data.get("title"),
            speaker_discord_id=data.get("speaker_discord_id"),
            speaker_nickname=data.get("speaker_nickname"),
            event_time=data.get("event_time"),
            form_id=data.get("form_id"))
