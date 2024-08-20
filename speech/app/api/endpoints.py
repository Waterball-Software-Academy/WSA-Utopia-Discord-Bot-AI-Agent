from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from speech.app.entities.speech_application import SpeechApplication
from speech.app.services.speech_service import SpeechService, PrefilledSpeechApplication, SpeechApplicationRequest

from speech.app.services.speech_service import Dependency as SpeechServiceDependency

router = APIRouter()


@router.get("/speeches/applications", response_model=PrefilledSpeechApplication)
async def start_speech_application_by_abstract(abstract: str, speaker_discord_id: str,
                                               speech_service: SpeechService = SpeechServiceDependency):
    application = await speech_service.start_speech_application_by_abstract(abstract, int(speaker_discord_id))
    return application


@router.post("/speeches/applications")
async def apply_speech(request: SpeechApplicationRequest,
                       speech_service: SpeechService = SpeechServiceDependency):
    saved_pending_application = await speech_service.apply_speech(request)
    return saved_pending_application
