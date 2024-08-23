import datetime

import discord
from discord import ScheduledEvent
from discord.ui import Button, View
from fastapi import Depends
from googleapiclient.discovery import build

from commons.discord_api import discord_api
from commons.errors import NotFoundException
from commons.google.calendar.google_calendar import GoogleCalendarServiceDependency, \
    WSA_OFFICIAL_CALENDAR_ID
from commons.utils import logging
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication, ApplicationReviewStatus
from speech.app.services.discord.utils import convert_to_minguo_format
from speech.app.services.models import ApplicationReviewResult

logger = logging.get_logger(__name__, diagnose=True)


async def _speech_application_template(application):
    return discord.Embed(
        description=f"""
## {application.title}

{application.description}
---
表單 ID：{application.id}
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
            await self.__handle_denied_speech_application(mod_review_interaction, application, dc_speaker,
                                                          embed_template)

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
        speech_update_dict = {"discord_event_id": str(event.id)}

        # 2. notify the event details to mod channel & speaker via discord
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
        speech_update_dict |= await self.schedule_event_to_all_channels(application, event)

        # 4. update the application with various event ids (e.g., discord event's id, google calendar event's id etc.)
        self.__speech_repo.update_speech_application(application.id, speech_update_dict)

    async def __schedule_event_via_discord(self, application: SpeechApplication) -> ScheduledEvent:
        speech_channel = await self.__wsa.fetch_channel(int(discord_api.speech_voice_channel_id))
        event = await self.__wsa.create_scheduled_event(
            name=f'{application.title} - By {application.speaker_name}',
            description=application.description,
            start_time=application.event_start_time,
            end_time=application.event_start_time + datetime.timedelta(minutes=application.duration_in_mins),
            location=speech_channel
        )
        logger.debug(f'[Scheduled event via discord] {{"event_id":"{event.id}"}}')
        return event

    async def schedule_event_to_all_channels(self, application: SpeechApplication, event: ScheduledEvent) -> dict:

        return await self.__schedule_event_on_wsa_official_google_calendar(application, event)
        # TODO: send notification via LINE OA

    async def __schedule_event_on_wsa_official_google_calendar(self, application: SpeechApplication,
                                                               event: ScheduledEvent) -> dict:
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
        calendar_id = WSA_OFFICIAL_CALENDAR_ID
        event_result = self.__google_calendar.events().insert(calendarId=calendar_id, body=new_event).execute()
        event_id = event_result.get('id')
        if event_result["status"] != 'confirmed':
            print("[Failed] can't create event on google calendar ")
        logger.debug(
            f'[Scheduled event to WSA Official Google Calendar] {{"event_id":"{event.id}", '
            f'"calendar_id":"{calendar_id}"}}')
        return {"google_calendar_official_event_id": event_id}

    async def __handle_denied_speech_application(self, mod_review_interaction: discord.Interaction,
                                                 application: SpeechApplication,
                                                 dc_speaker: discord.User,
                                                 embed_template: discord.Embed):
        # 1. TODO Delete event from WSA's pending events google calendar
        self.__speech_repo.delete_by_id(application.id)
        logger.trace("Deleted speech application from DB")

        # 2. Notify the speaker
        embed_template.title = "抱歉，您的活動申請沒有通過審查，請再提交一次"
        embed_template.description = embed_template.description + (f'---\n拒絕原因：{application.deny_reason}\n'
                                                                   f'### 請修改後再提交一次，非常感謝，若有疑問歡迎至社群中提問 🙏。')
        embed_template.colour = discord.Colour.red()
        await dc_speaker.send(embed=embed_template)
        logger.trace("Sent a defined notification to Speaker.")


def get_speech_application_review_result_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                                 discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
                                                 speech_application_repo=SpeechRepoDependency,
                                                 google_calendar_service=GoogleCalendarServiceDependency):
    return SpeechApplicationReviewResultHandler(discord_app, discord_wsa, speech_application_repo,
                                                google_calendar_service)


Dependency = Depends(get_speech_application_review_result_handler)
