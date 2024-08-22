
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


@router.get("/applications/{id}")
async def get_speech_application(id: str,
                                 speech_service: SpeechService = SpeechServiceDependency):
    application = await speech_service.find_speech_application(id)
    return application


@router.post("/applications/webhook/cal.com")
async def webhook_from_cal_com(body: dict, speech_service: SpeechService = SpeechServiceDependency):
    payload = body['payload']
    responses = payload['responses']
    request = SpeechApplicationRequest(
        title=responses['title']['value'],
        description=responses['notes']['value'],
        speaker_name=responses.get('name', {}).get('value'),
        cal_booking_uid=payload['uid'],
        cal_booking_id=payload['bookingId'],
        cal_location=payload['location'],
        speaker_attendee_email=payload['attendees'][0]['email'],
        event_start_time=payload['startTime'],
        event_end_time=payload['endTime'],
        duration_in_mins=payload['length'],
        speaker_discord_id=responses.get('speakerDiscordId', {}).get('value'), )

    await speech_service.apply_speech(request)
