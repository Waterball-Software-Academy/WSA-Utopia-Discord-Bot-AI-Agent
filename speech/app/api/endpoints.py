from fastapi import APIRouter

from speech.app.services.speech_service import SpeechService, PrefilledSpeechApplication

from speech.app.services.speech_service import Dependency as SpeechServiceDependency

router = APIRouter()


@router.get("/speeches/applications", response_model=PrefilledSpeechApplication)
async def start_speech_application_by_abstract(abstract: str, speaker_discord_id: str,
                                               speech_service: SpeechService = SpeechServiceDependency):
    application = await speech_service.start_speech_application_by_abstract(abstract, int(speaker_discord_id))
    return application
