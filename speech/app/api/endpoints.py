import json

from fastapi import APIRouter
from fastapi import BackgroundTasks

from commons.utils.logging import get_logger
from speech.app.services.speech_service import Dependency as SpeechServiceDependency
from speech.app.services.speech_service import SpeechService, PrefilledSpeechApplication, SpeechApplicationRequest

router = APIRouter()

logger = get_logger("Speech's Endpoints", diagnose=True)


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
async def webhook_from_cal_com(body: dict, background_tasks: BackgroundTasks,
                               speech_service: SpeechService = SpeechServiceDependency):
    event = body['triggerEvent']
    payload = body['payload']
    responses = payload['responses']
    if event == "BOOKING_CREATED":
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

        logger.info("[cal.com Webhook (BOOKING_CREATED)] "
                    f'{{"title": "{request.title}", '
                    f'"description": "{request.description}", '
                    f'"speaker_name": "{request.speaker_name}", '
                    f'"event_start_time": "{request.event_start_time.isoformat()}", '
                    f'"event_end_time": "{request.event_end_time.isoformat()}", '
                    f'"duration_in_mins": {request.duration_in_mins}, '
                    f'"cal_booking_id": {request.cal_booking_id}, '
                    f'"cal_booking_uid": "{request.cal_booking_uid}", '
                    f'"cal_location": "{request.cal_location}", '
                    f'"speaker_discord_id": "{request.speaker_discord_id}", '
                    f'"speaker_attendee_email": "{request.speaker_attendee_email}"'
                    f'}}'
                    )
        background_tasks.add_task(speech_service.apply_speech, request)
    elif event == "BOOKING_CANCELLED":
        cal_booking_id = payload.get('bookingId')
        cal_uid = payload.get('uid')
        logger.info("[cal.com Webhook (BOOKING_CANCELLED)] "
                    f'{{"title": "{payload["title"]}", '
                    f'"cal_uid": "{cal_uid}", '
                    f'"cal_booking_id": "{cal_booking_id}", '
                    f'"cancellationReason": "{payload.get("cancellationReason")}"}}'
                    )
        background_tasks.add_task(speech_service.cancel_speech_application, cal_uid)
    else:
        pass
