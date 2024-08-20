import discord
from fastapi import Depends
from pydantic import BaseModel

import commons.discord_api.discord_api as discord_api


class PrefilledSpeechApplication(BaseModel):
    title: str
    description: str
    speaker_name: str


class SpeechService:
    def __init__(self, wsa: discord.Guild = discord_api.WsaGuildDependency):
        self.__wsa = wsa

    async def start_speech_application_by_abstract(self, abstract: str,
                                                   speaker_discord_id: int) -> PrefilledSpeechApplication:
        name = await self.__get_speaker_name_from_discord_wsa(speaker_discord_id)
        return await self.__generate_prefilled_application(abstract, name)

    async def __get_speaker_name_from_discord_wsa(self, speaker_discord_id: int) -> str:
        discord_user = await self.__wsa.fetch_member(speaker_discord_id)
        return discord_user.display_name

    async def __generate_prefilled_application(self, abstract: str, speaker_name: str) -> PrefilledSpeechApplication:
        # TODO: generate application by abstract with AI
        return PrefilledSpeechApplication(title='TODO', description='TODO', speaker_name=speaker_name)


__instance = None


def get_language_service(discord_wsa: discord.Guild = discord_api.WsaGuildDependency):
    global __instance
    __instance = SpeechService(discord_wsa)
    return __instance


Dependency = Depends(get_language_service)
