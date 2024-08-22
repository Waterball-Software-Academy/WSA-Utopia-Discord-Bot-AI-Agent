from datetime import datetime

import discord
from fastapi import Depends
from pydantic import BaseModel

import commons.discord_api.discord_api as discord_api
from commons.utils.logging import get_logger
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication
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
                 speech_application_repo: SpeechApplicationRepository, openai_agent: OpenAIModelClient,
                 review_speech_application_handler: ReviewSpeechApplicationHandler):
        self.__discord_app = discord_app
        self.__wsa = wsa
        self.__speech_application_repo = speech_application_repo
        self.__openai_agent = openai_agent
        self.__review_speech_application_handler = review_speech_application_handler

    async def start_speech_application_by_abstract(self, abstract: str,
                                                   speaker_discord_id: int) -> PrefilledSpeechApplication:
        name = await self.__get_speaker_name_from_discord_wsa(speaker_discord_id)
        return await self.__generate_prefilled_application(abstract, name)

    async def __get_speaker_name_from_discord_wsa(self, speaker_discord_id: int) -> str:
        discord_user = await self.__wsa.fetch_member(speaker_discord_id)
        return discord_user.display_name

    async def __generate_prefilled_application(self, abstract: str, speaker_name: str) -> PrefilledSpeechApplication:
        event_info = await self.__openai_agent.generate_from_abstract(abstract)
        return PrefilledSpeechApplication(title=event_info.title, description=event_info.description,
                                          speaker_name=speaker_name)

    async def apply_speech(self, request: SpeechApplicationRequest) -> dict:
        logger.info(f'[Apply speech] {{"id": "{request.cal_booking_id}", "title": "{request.title}""}}')
        application = request.to_entity()
        saved = self.__speech_application_repo.save(application)
        await self.__review_speech_application_handler.review(application)
        return saved.to_dict()

    async def find_speech_application(self, id: str) -> dict:
        # TODO: not found handling
        speech_application = self.__speech_application_repo.find_by_id(id)
        return speech_application.to_dict()


__instance = None


def init_speech_service(
        discord_app: discord.Bot = discord_api.DiscordAppDependency,
        discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
        speech_application_repo: SpeechApplicationRepository = SpeechRepoDependency,
        open_ai_client: OpenAIModelClient = OpenAIClientDependency,
        review_speech_application_handler=ReviewSpeechApplicationHandlerDependency):
    global __instance
    __instance = SpeechService(discord_app, discord_wsa, speech_application_repo, open_ai_client,
                               review_speech_application_handler)
    return __instance


Dependency = Depends(init_speech_service)
