import datetime

import discord
from discord import ScheduledEvent
from fastapi import Depends
from googleapiclient.discovery import build

from commons.discord_api import discord_api
from commons.errors import NotFoundException
from commons.google.calendar.google_calendar import GoogleCalendarServiceDependency, \
    WSA_CALENDAR_ID
from speech.app.data.speech_repo import Dependency as SpeechRepoDependency, SpeechApplicationRepository
from speech.app.entities.speech_application import SpeechApplication
from speech.app.services.models import ApplicationReviewResult


class SpeechApplicationReviewResultHandler:
    def __init__(self, discord_app: discord.Bot,
                 wsa: discord.Guild,
                 speech_repo: SpeechApplicationRepository,
                 google_calendar: build):
        self.__wsa = wsa
        self.__speech_repo = speech_repo
        self.__discord_app = discord_app
        self.__google_calendar = google_calendar

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
            await self.sync_event_to_all_channels(application, event)
        else:
            await dc_speaker.send(f"你的短講被拒絕了")

    async def __schedule_discord_event_for_speech(self, application: SpeechApplication) -> ScheduledEvent:
        speech_channel = await self.__wsa.fetch_channel(int(discord_api.speech_voice_channel_id))
        event = await self.__wsa.create_scheduled_event(
            name=f'{application.title} - By {application.speaker_name}',
            description=application.description,
            start_time=application.event_start_time,
            end_time=application.event_start_time + datetime.timedelta(minutes=application.duration_in_mins),
            location=speech_channel
        )
        return event

    async def sync_event_to_all_channels(self, application: SpeechApplication, event: ScheduledEvent):
        await self.sync_event_via_google_calendar(application, event)

    async def sync_event_via_google_calendar(self, application: SpeechApplication, event: ScheduledEvent):

        new_event = {
            'summary': f'{application.title}',
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
            'attendees': [],
            'reminders': {
                'useDefault': True,
            },
        }

        # Insert the event into the calendar
        calendar_id = WSA_CALENDAR_ID
        event_result = self.__google_calendar.events().insert(calendarId=calendar_id, body=new_event).execute()
        if event_result["status"] is not 'confirmed':
            print("[Failed] can't create event on google calendar ")
        print(event_result)  # TODO:check if it failed, should log


def get_speech_application_review_result_handler(discord_app: discord.Bot = discord_api.DiscordAppDependency,
                                                 discord_wsa: discord.Guild = discord_api.WsaGuildDependency,
                                                 speech_application_repo=SpeechRepoDependency,
                                                 google_calendar_service=GoogleCalendarServiceDependency):
    return SpeechApplicationReviewResultHandler(discord_app, discord_wsa, speech_application_repo,
                                                google_calendar_service)


Dependency = Depends(get_speech_application_review_result_handler)
