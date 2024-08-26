import asyncio
from datetime import datetime

import discord
import googleapiclient.discovery
from fastapi import Depends
from pydantic import BaseModel

import commons.discord_api.discord_api as discord_api
from commons.google.calendar.google_calendar import WSA_OFFICIAL_CALENDAR_ID, GoogleCalendarServiceDependency
from commons.utils.logging import get_logger
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus
from speech.app.services.basic_openai_agent import OpenAIModelClient, OpenAIClientDependency
from speech.app.services.discord.ReviewSpeechApplicationHandler import \
    Dependency as ReviewSpeechApplicationHandlerDependency, \
    ReviewSpeechApplicationHandler

logger = get_logger("speech_service", diagnose=True)


class PrefilledSpeechApplication(BaseModel):
    title: str
    description: str
    speaker_name: str


class SpeechApplicationRequest(BaseModel):
    title: str
    description: str
    speaker_name: str
    event_start_time: datetime
    event_end_time: datetime
    duration_in_mins: int
    cal_booking_id: int
    cal_booking_uid: str
    cal_location: str
    speaker_discord_id: str
    speaker_attendee_email: str

    def to_entity(self):
        return SpeechApplication(
            _id=self.cal_booking_uid,
            title=self.title,
            description=self.description,
            speaker_name=self.speaker_name,
            event_start_time=self.event_start_time,
            event_end_time=self.event_end_time,
            duration_in_mins=self.duration_in_mins,
            cal_booking_id=self.cal_booking_id,
            cal_booking_uid=self.cal_booking_uid,
            speaker_discord_id=self.speaker_discord_id,
            speaker_attendee_email=self.speaker_attendee_email)


class SpeechService:
    def __init__(self, discord_app: discord.Bot, wsa: discord.Guild,
                 speech_application_repo: SpeechApplicationRepository,
                 openai_agent: OpenAIModelClient,
                 google_calendar: googleapiclient.discovery.build,
                 review_speech_application_handler: ReviewSpeechApplicationHandler):
        self.__discord_app = discord_app
        self.__wsa = wsa
        self.__speech_application_repo = speech_application_repo
        self.__openai_agent = openai_agent
        self.__google_calendar = google_calendar
        self.__review_speech_application_handler = review_speech_application_handler

    async def start_speech_application_by_abstract(self, abstract: str,
                                                   speaker_discord_id: int) -> PrefilledSpeechApplication:
        name = await self.__get_speaker_name_from_discord_wsa(speaker_discord_id)
        return await self.__generate_prefilled_application(abstract, name)

    async def __get_speaker_name_from_discord_wsa(self, speaker_discord_id: int) -> str:
        discord_user = await discord_api.execute_task_and_get_result(self.__wsa.fetch_member, speaker_discord_id)
        return discord_user.display_name

    async def __generate_prefilled_application(self, abstract: str, speaker_name: str) -> PrefilledSpeechApplication:
        event_info = await self.__openai_agent.generate_from_abstract(abstract)
        return PrefilledSpeechApplication(title=event_info.title, description=event_info.description,
                                          speaker_name=speaker_name)

    async def apply_speech(self, request: SpeechApplicationRequest) -> dict:
        application = request.to_entity()
        logger.info(f'[Apply speech] {{"id": "{application.id}", "title": "{application.title}""}}')
        saved = self.__speech_application_repo.save(application)
        logger.trace(f'Saved Speech Application into DB.')
        await self.__review_speech_application_handler.review(application)
        return saved.to_dict()

    async def find_speech_application(self, id: str) -> dict:
        # TODO: not found handling
        speech_application = self.__speech_application_repo.find_by_id(id)
        return speech_application.to_dict()

    async def cancel_speech_application(self, id: str):
        logger.info(f'[Cancel Speech Application] {{"id": "{id}"}}')
        application = self.__speech_application_repo.find_by_id(id)
        logger.debug(f'Speech Application: {{"discord_event_id"="{application.discord_event_id}", '
                     f'"google_calendar_official_event_id="{application.google_calendar_official_event_id}"}}')
        self.__speech_application_repo.delete_by_id(id)
        if application.application_review_status == ApplicationReviewStatus.ACCEPTED:
            await asyncio.gather(self.__delete_discord_event(application),
                                 self.__delete_event_from_wsa_official_google_calendar(application))

    async def __delete_discord_event(self, application: SpeechApplication):
        discord_event = await self.__wsa.fetch_scheduled_event(int(application.discord_event_id))
        logger.debug(f'[Deleting discord event] {{"event_id":"{discord_event.id}"}}')
        await discord_event.delete()
        logger.trace(f"Deleted Speech Application's event from Discord.")

    async def __delete_event_from_wsa_official_google_calendar(self, application: SpeechApplication):
        self.__google_calendar.events().delete(calendarId=WSA_OFFICIAL_CALENDAR_ID,
                                               eventId=application.google_calendar_official_event_id).execute()
        logger.trace(f"Deleted Speech Application's event from WSA Official Google Calendar.")


__instance = None


def init_speech_service(
        discord_app: discord.Bot = discord_api.DiscordAppDependency,
        discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
        speech_application_repo: SpeechApplicationRepository = SpeechRepoDependency,
        open_ai_client: OpenAIModelClient = OpenAIClientDependency,
        google_calendar: googleapiclient.discovery.build = GoogleCalendarServiceDependency,
        review_speech_application_handler=ReviewSpeechApplicationHandlerDependency):
    global __instance
    __instance = SpeechService(discord_app, discord_wsa, speech_application_repo, open_ai_client, google_calendar,
                               review_speech_application_handler)
    return __instance


Dependency = Depends(init_speech_service)
