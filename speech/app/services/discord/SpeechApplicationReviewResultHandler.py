import datetime

import discord
from discord import ScheduledEvent
from fastapi import Depends

from commons.discord_api import discord_api
from commons.errors import NotFoundException
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.services.models import ApplicationReviewResult


class SpeechApplicationReviewResultHandler:
    def __init__(self, discord_app: discord.Bot,
                 wsa: discord.Guild,
                 speech_repo: SpeechApplicationRepository):
        self.__wsa = wsa
        self.__speech_repo = speech_repo
        self.__discord_app = discord_app

    async def handle(self, speech_id: str,
                     speaker_id: str,
                     review_result: ApplicationReviewResult):
        dc_speaker = await self.__discord_app.fetch_user(int(speaker_id))
        if dc_speaker is None:
            raise NotFoundException("User (Discord)", dc_speaker)

        if review_result.is_accepted():
            await dc_speaker.send(f"恭喜你，你的短講已經通過審查了！")
            application = self.__speech_repo.find_by_id(speech_id)
            if application is None:
                raise NotFoundException("Speech Application", application)
            event = await self.__schedule_discord_event_for_speech(application)
            mod_speech_application_review_channel = self.__wsa.get_channel(
                int(discord_api.mod_speech_application_review_channel_id))
            await mod_speech_application_review_channel.send(event.url)
            await dc_speaker.send(event.url)
        else:
            await dc_speaker.send(f"你的短講被拒絕了")

    async def __schedule_discord_event_for_speech(self, application) -> ScheduledEvent:
        speech_channel = await self.__wsa.fetch_channel(int(discord_api.speech_voice_channel_id))
        event = await self.__wsa.create_scheduled_event(
            name=f'{application.title} - By {application.speaker_name}',
            description=application.description,
            start_time=application.event_start_time,
            end_time=application.event_start_time + datetime.timedelta(minutes=application.duration_in_mins),
            location=speech_channel
        )
        return event


def get_speech_application_review_result_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                                 discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
                                                 speech_application_repo=SpeechRepoDependency):
    return SpeechApplicationReviewResultHandler(discord_app, discord_wsa, speech_application_repo)


Dependency = Depends(get_speech_application_review_result_handler)
