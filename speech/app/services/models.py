from typing import Optional

from speech.app.entities.speech_application import ApplicationReviewStatus


class ApplicationReviewResult:
    def __init__(self, status: ApplicationReviewStatus, deny_reason: Optional[str] = None):
        self.status = status
        self.deny_reason = deny_reason

    def is_accepted(self) -> bool:
        return self.status == ApplicationReviewStatus.ACCEPTED
