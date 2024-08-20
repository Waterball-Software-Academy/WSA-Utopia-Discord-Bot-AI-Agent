from datetime import datetime

import discord
from fastapi import Depends
from pydantic import BaseModel

import commons.discord_api.discord_api as discord_api
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication
from speech.app.services.basic_openai_agent import OpenAIModelClient, OpenAIClientDependency
from speech.app.services.discord.ReviewSpeechApplicationHandler import \
    Dependency as ReviewSpeechApplicationHandlerDependency, \
    ReviewSpeechApplicationHandler


class PrefilledSpeechApplication(BaseModel):
    title: str
    description: str
    speaker_name: str


class SpeechApplicationRequest(BaseModel):
    speaker_discord_id: str
    title: str
    description: str
    speaker_name: str
    event_start_time: datetime
    duration_in_mins: int


class SpeechApplicationResponse(BaseModel):
    id: str
    title: str
    description: str
    speaker_name: str
    speaker_discord_id: str
    event_start_time: float
    duration_in_mins: int
    application_review_status: str
    apply_time: float


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

    async def apply_speech(self, request: SpeechApplicationRequest):
        # TODO: validation?
        application = SpeechApplication(request.title, request.speaker_discord_id,
                                        request.speaker_name, request.description, request.event_start_time,
                                        request.duration_in_mins)
        saved = self.__speech_application_repo.save(application)
        await self.__review_speech_application_handler.review(application)
        return SpeechApplicationResponse(
            id=saved._id,
            title=saved.title,
            description=saved.description,
            speaker_name=saved.speaker_name,
            speaker_discord_id=saved.speaker_discord_id,
            event_start_time=saved.event_start_time.timestamp(),
            duration_in_mins=saved.duration_in_mins,
            application_review_status=saved.application_review_status,
            apply_time=saved.apply_time.timestamp()

        )


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
