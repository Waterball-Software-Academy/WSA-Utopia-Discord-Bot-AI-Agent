import discord
from fastapi import Depends

from commons.discord_api import discord_api
from speech.app.entities.speech_application import SpeechApplication


class SpeechApplicationReviewView(discord.ui.View):
    @discord.ui.button(label="通過申請", style=discord.ButtonStyle.success, emoji="🙅")
    async def accept_application(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Accept")

    @discord.ui.button(label="拒絕申請", style=discord.ButtonStyle.primary, emoji="🙆")
    async def deny_application(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("Deny")


class WsaModDiscordSpeechHandler:
    def __init__(self, discord_app: discord.Bot,
                 wsa: discord.Guild):
        self.__wsa = wsa
        self.__discord_app = discord_app

    async def handle_new_speech_application_notification(self, application: SpeechApplication):
        # 1. notify the speaker via DM
        dc_speaker = await self.__discord_app.fetch_user(int(application.speaker_discord_id))
        await dc_speaker.send("Hi 你的演講已經申請完畢囉")

        # 2. ask the mods to review this application
        channel = await self.__discord_app.fetch_channel(discord_api.mod_speech_application_review_channel_id)
        embed = discord.Embed(
            title="短講申請審查",
            description=f"## {application.title}\n\n {application.description}\n\n講者：<@{application.speaker_discord_id}>",
            color=discord.Color.blurple()
        )

        view = SpeechApplicationReviewView()
        await channel.send(embed=embed, view=view)


def get_wsa_mod_discord_speech_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                       discord_wsa: discord.Guild = discord_api.WsaGuildDependency):
    return WsaModDiscordSpeechHandler(discord_app, discord_wsa)


Dependency = Depends(get_wsa_mod_discord_speech_handler)
