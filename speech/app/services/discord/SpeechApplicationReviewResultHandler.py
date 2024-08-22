import datetime

import discord
from discord import ScheduledEvent
from discord.ui import Button, View
from fastapi import Depends
from googleapiclient.discovery import build

from commons.discord_api import discord_api
from commons.errors import NotFoundException
from commons.google.calendar.google_calendar import GoogleCalendarServiceDependency, \
    WSA_PROD_CALENDAR_ID
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication
from speech.app.services.discord.utils import convert_to_minguo_format
from speech.app.services.models import ApplicationReviewResult


async def _speech_application_template(application):
    return discord.Embed(
        description=f"""
## {application.title}

{application.description}
---
表單 ID：{application._id}
講者：<@{application.speaker_discord_id}>
時間：{convert_to_minguo_format(application.event_start_time)}
時長：{application.duration_in_mins // 60} 小時 {application.duration_in_mins % 60} 分鐘
""",
    )


class SpeechApplicationReviewResultHandler:
    def __init__(self, discord_app: discord.Bot,
                 wsa: discord.Guild,
                 speech_repo: SpeechApplicationRepository,
                 google_calendar: build):
        self.__wsa = wsa
        self.__speech_repo = speech_repo
        self.__discord_app = discord_app
        self.__google_calendar = google_calendar

    async def handle(self, mod_review_interaction: discord.Interaction,
                     speech_id: str, speaker_id: str,
                     review_result: ApplicationReviewResult):
        application, dc_speaker = await self.__fetch_entities(speech_id, speaker_id)
        embed_template = await _speech_application_template(application)
        if review_result.is_accepted():
            await self.__handle_accepted_speech_application(mod_review_interaction, application, dc_speaker,
                                                            embed_template)
        else:
            embed_template.title = "抱歉，您的活動申請沒有通過審查，請再提交一次"
            embed_template.description = embed_template.description + (f'---\n拒絕原因：{application.deny_reason}\n'
                                                                       f'### 請修改後再提交一次，非常感謝，若有疑問歡迎至社群中提問 🙏。')
            embed_template.colour = discord.Colour.red()
            await dc_speaker.send(embed=embed_template)

    async def __fetch_entities(self, speech_id: str, speaker_id: str) -> [SpeechApplication, discord.User]:
        application = self.__speech_repo.find_by_id(speech_id)
        if application is None:
            raise NotFoundException("Speech Application", application)
        dc_speaker = await self.__discord_app.fetch_user(int(speaker_id))
        if dc_speaker is None:
            raise NotFoundException("User (Discord)", dc_speaker)
        return application, dc_speaker

    async def __handle_accepted_speech_application(self, mod_review_interaction: discord.Interaction,
                                                   application: SpeechApplication, dc_speaker: discord.User,
                                                   embed: discord.Embed):
        # 1. schedule event via discord
        event = await self.__schedule_event_via_discord(application)

        # 2. notify the event details to mod channel & speaker via discord
        mod_speech_application_review_channel = await self.__wsa.fetch_channel(
            int(discord_api.mod_speech_application_review_channel_id))
        original_response = await mod_review_interaction.original_response()
        await original_response.edit(f"{original_response.content}\n{event.url}")

        embed.title = "恭喜你！您的活動時間已經安排！一起享受費曼學習吧！"
        embed.colour = discord.Colour.brand_green()
        button = Button(label="查看/修改活動", url="https://www.example.com")
        view = View()
        view.add_item(button)
        await dc_speaker.send(embed=embed, view=view)
        await dc_speaker.send(
            f'活動連結：{event.url} ，記得提早 5 分鐘入場，我也會提早 5 分鐘入場來協助您處理逐字稿，並且我會全程擔任您的最佳聽眾喔！請自在分享 👌🏻👌🏻👌🏻')

        # 3. schedule event to all channels (google calendar, LINE OA...)
        await self.schedule_event_to_all_channels(application, event)

    async def __schedule_event_via_discord(self, application: SpeechApplication) -> ScheduledEvent:
        speech_channel = await self.__wsa.fetch_channel(int(discord_api.speech_voice_channel_id))
        event = await self.__wsa.create_scheduled_event(
            name=f'{application.title} - By {application.speaker_name}',
            description=application.description,
            start_time=application.event_start_time,
            end_time=application.event_start_time + datetime.timedelta(minutes=application.duration_in_mins),
            location=speech_channel
        )
        return event

    async def schedule_event_to_all_channels(self, application: SpeechApplication, event: ScheduledEvent):
        await self.__schedule_event_on_wsa_prod_google_calendar(application, event)

    async def __schedule_event_on_wsa_prod_google_calendar(self, application: SpeechApplication, event: ScheduledEvent):
        new_event = {
            'summary': f'{application.title} - By {application.speaker_name}',
            'location': f'{event.url}',
            'description': f'{application.description}',
            'start': {
                'dateTime': f'{event.start_time.isoformat()}',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': f'{event.end_time.isoformat()}',
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        # Insert the event into the calendar
        calendar_id = WSA_PROD_CALENDAR_ID
        event_result = self.__google_calendar.events().insert(calendarId=calendar_id, body=new_event).execute()
        if event_result["status"] != 'confirmed':
            print("[Failed] can't create event on google calendar ")


def get_speech_application_review_result_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                                 discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
                                                 speech_application_repo=SpeechRepoDependency,
                                                 google_calendar_service=GoogleCalendarServiceDependency):
    return SpeechApplicationReviewResultHandler(discord_app, discord_wsa, speech_application_repo,
                                                google_calendar_service)


Dependency = Depends(get_speech_application_review_result_handler)
