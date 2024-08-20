from fastapi import APIRouter

from speech.app.services.speech_service import Dependency as SpeechServiceDependency
from speech.app.services.speech_service import SpeechService, PrefilledSpeechApplication, SpeechApplicationRequest

router = APIRouter()


@router.get("/applications", response_model=PrefilledSpeechApplication)
async def start_speech_application_by_abstract(abstract: str, speaker_discord_id: str,
                                               speech_service: SpeechService = SpeechServiceDependency):
    application = await speech_service.start_speech_application_by_abstract(abstract, int(speaker_discord_id))
    return application


@router.post("/applications")
async def apply_speech(request: SpeechApplicationRequest,
                       speech_service: SpeechService = SpeechServiceDependency):
    saved_pending_application = await speech_service.apply_speech(request)
    return saved_pending_application
