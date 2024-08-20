from fastapi import Depends

from commons.events.event_bus import EventBus
from speech.app.events import NEW_SPEECH_APPLIED
from speech.app.services.discord import ReviewSpeechApplicationHandler


def get_event_bus(review_speech_application_handler=ReviewSpeechApplicationHandler.Dependency) -> EventBus:
    event_bus = EventBus()
    # Register all event listeners here
    event_bus.subscribe(NEW_SPEECH_APPLIED, review_speech_application_handler)
    return event_bus


EventBusDependency = Depends(get_event_bus)
