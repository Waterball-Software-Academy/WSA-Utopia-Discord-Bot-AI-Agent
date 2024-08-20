from datetime import datetime
from typing import Optional

import discord
from fastapi import Depends
from speech.app.services.discord.SpeechApplicationReviewResultHandler import \
    Dependency as SpeechApplicationReviewResultHandlerDependency, SpeechApplicationReviewResultHandler
from commons.discord_api import discord_api
from commons.errors import NotFoundException
from speech.app.data.speech_repo import SpeechApplicationRepository
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus
from speech.app.services.discord.utils import convert_to_minguo_format
from speech.app.services.models import ApplicationReviewResult


async def _handle_application_review_result(review_result_handler: SpeechApplicationReviewResultHandler,
                                            embed: discord.Embed,
                                            interaction: discord.Interaction,
                                            speaker_id: str, speech_id: str,
                                            updated_title: str, response_message: str,
                                            review_result: ApplicationReviewResult):
    # 1. issue review result
    await review_result_handler.handle(speech_id, speaker_id, review_result)
    # 2. effect embed message interaction to indicate the result
    embed.title = updated_title
    embed.description = (f"""{embed.description}---
審查者：<@{interaction.user.id}>
審查時間：{convert_to_minguo_format(datetime.now())}
""")
    if review_result.is_accepted():
        embed.colour = discord.Color.green()
    else:
        embed.description = f"{embed.description}拒絕原因：{review_result.deny_reason}"
        embed.colour = discord.Color.red()
    await interaction.message.edit(embed=embed, view=None)
    await interaction.respond(response_message, ephemeral=True)


class DenyReasonModal(discord.ui.Modal):
    def __init__(self, review_result_handler: SpeechApplicationReviewResultHandler, speech_id: str, speaker_id: str,
                 speech_application_repository: SpeechApplicationRepository,
                 embed: discord.Embed):
        super().__init__(title="拒絕申請")
        self.__review_result_handler = review_result_handler
        self.__speech_id = speech_id
        self.__speaker_id = speaker_id
        self.__speech_application_repository = speech_application_repository
        self.__embed = embed
        self.input_field = discord.ui.InputText(label="請輸入拒絕申請的理由", placeholder="請輸入拒絕申請的理由...")
        self.add_item(self.input_field)

    async def callback(self, interaction: discord.Interaction):
        deny_reason = self.input_field.value
        try:
            self.__speech_application_repository.update_speech_application_review_status(self.__speech_id,
                                                                                         ApplicationReviewStatus.DENIED,
                                                                                         deny_reason)
            await _handle_application_review_result(self.__review_result_handler, self.__embed, interaction,
                                                    self.__speaker_id, self.__speech_id,
                                                    "🙅 短講申請審查（已拒絕審查）",
                                                    f"✅ 短講申請 ({self.__speech_id}) 已被拒絕。",
                                                    review_result=ApplicationReviewResult(
                                                        ApplicationReviewStatus.DENIED, deny_reason=deny_reason))
            print(f"Speech (id={self.__speech_id}) denied.")
        except NotFoundException as e:
            print(e)
            await interaction.respond(f"Error: {str(e)}", ephemeral=True)


class SpeechApplicationReviewView(discord.ui.View):

    def __init__(self, review_result_handler: SpeechApplicationReviewResultHandler, embed: discord.Embed,
                 speech_application_repository: SpeechApplicationRepository):
        super().__init__()
        self.__review_result_handler = review_result_handler
        self.__embed = embed
        self.__speech_application_repository = speech_application_repository

    @discord.ui.button(label="通過申請", style=discord.ButtonStyle.success, emoji="🙆")
    async def accept_application(self, button: discord.ui.Button, interaction: discord.Interaction):
        speech_id = button.speech_id
        speaker_id = button.speaker_id

        try:
            self.__speech_application_repository.update_speech_application_review_status(speech_id,
                                                                                         ApplicationReviewStatus.ACCEPTED)
            await _handle_application_review_result(self.__review_result_handler, self.__embed, interaction,
                                                    speaker_id, speech_id,
                                                    "🙆 短講申請審查（已通過審查）",
                                                    f"✅ 短講申請 ({speech_id}) 已通過審查。",
                                                    review_result=ApplicationReviewResult(
                                                        ApplicationReviewStatus.ACCEPTED))
            print(f"Speech (id={button.speech_id}) accepted.")
        except NotFoundException as e:
            print(e)
            await interaction.respond(f"Error: {str(e)}", ephemeral=True)

    @discord.ui.button(label="拒絕申請", style=discord.ButtonStyle.primary, emoji="🙅")
    async def deny_application(self, button: discord.ui.Button, interaction: discord.Interaction):
        speech_id = button.speech_id
        speaker_id = button.speaker_id
        try:
            await interaction.response.send_modal(
                DenyReasonModal(self.__review_result_handler, speech_id, speaker_id,
                                self.__speech_application_repository,
                                self.__embed))
        except NotFoundException as e:
            print(e)
            await interaction.respond(f"Error: {str(e)}", ephemeral=True)


class ReviewSpeechApplicationHandler:
    def __init__(self,
                 speech_application_review_result_handler: SpeechApplicationReviewResultHandlerDependency,
                 discord_app: discord.Bot,
                 wsa: discord.Guild,
                 speech_repo: SpeechRepoDependency):
        self.review_result_handler = speech_application_review_result_handler
        self.__wsa = wsa
        self.__speech_repo = speech_repo
        self.__discord_app = discord_app

    async def review(self, application: SpeechApplication):
        # 1. notify the speaker via DM
        dc_speaker = await self.__discord_app.fetch_user(int(application.speaker_discord_id))
        await dc_speaker.send("Hi 你的演講已經申請完畢囉")

        # 2. ask the mods to review this application
        channel = await self.__discord_app.fetch_channel(discord_api.mod_speech_application_review_channel_id)
        embed = discord.Embed(
            title="短講申請審查",
            description=f"""
## {application.title}

{application.description}
---
表單 ID：{application._id}
講者：<@{application.speaker_discord_id}>
時間：{convert_to_minguo_format(application.event_start_time)}
時長：{application.duration_in_mins // 60} 小時 {application.duration_in_mins % 60} 分鐘
""",
            color=discord.Color.blurple()
        )

        view = SpeechApplicationReviewView(self.review_result_handler, embed, self.__speech_repo)

        # Carry relevant data so that when handling the button event later, you can identify the speech, speaker,
        # ... and so on.
        for item in view.children:
            item.speech_id = application._id
            item.speaker_id = application.speaker_discord_id
        await channel.send(embed=embed, view=view)


def get_review_speech_application_handler(
        speech_application_review_result_handler=SpeechApplicationReviewResultHandlerDependency,
        discord_app: discord.Bot = discord_api.DiscordAppDependency,
        discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
        speech_application_repo=SpeechRepoDependency):
    return ReviewSpeechApplicationHandler(speech_application_review_result_handler, discord_app, discord_wsa,
                                          speech_application_repo)


Dependency = Depends(get_review_speech_application_handler)
