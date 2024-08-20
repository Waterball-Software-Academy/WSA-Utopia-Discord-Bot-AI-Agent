from typing import Optional

import discord
from fastapi import Depends

from commons.discord_api import discord_api
from commons.errors import NotFoundException
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency
from speech.app.entities.speech_application import ApplicationReviewStatus
from speech.app.services.models import ApplicationReviewResult


class SpeechApplicationReviewResultHandler:
    def __init__(self, discord_app: discord.Bot,
                 wsa: discord.Guild,
                 speech_repo: SpeechRepoDependency):
        self.__wsa = wsa
        self.__speech_repo = speech_repo
        self.__discord_app = discord_app

    async def handle(self, speech_id: str,
                     speaker_id: str,
                     review_result: ApplicationReviewResult):
        dc_speaker = await self.__discord_app.fetch_user(int(speaker_id))
        if dc_speaker is None:
            raise NotFoundException("User (Discord)", dc_speaker)
        await dc_speaker.send(
            f"Hi 你的演講已經{'通過' if review_result.status == ApplicationReviewStatus.ACCEPTED else f'被拒絕，理由是 {review_result.deny_reason}'}")
        print("Test")
        # application = self.__speech_repo.find_by_id(speech_id)
        # if application is None:
        #     raise NotFoundException("Speech Application", application)


def get_speech_application_review_result_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                                 discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
                                                 speech_application_repo=SpeechRepoDependency):
    return SpeechApplicationReviewResultHandler(discord_app, discord_wsa, speech_application_repo)


Dependency = Depends(get_speech_application_review_result_handler)
