import datetime
import os.path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from commons.utils.os import get_project_root

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_FILE = "waterball-software-academy.google.credentials.json"

WSA_PROD_CALENDAR_ID = os.getenv('WSA_PROD_CALENDAR_ID')

__project_root = get_project_root()
__target_credentials_path = os.path.join(__project_root, CREDENTIALS_FILE)

if not os.path.exists(__target_credentials_path):
    print("Can't find your google.credentials file. The file is git-ignored, remember to download it manually.")
    raise FileNotFoundError(__target_credentials_path)

google_calendar_service: Optional[build] = None


async def connect_to_service() -> build:
    try:
        global google_calendar_service
        google_calendar_service = build("calendar", "v3",
                                        credentials=service_account.Credentials.from_service_account_file(
                                            __target_credentials_path, scopes=SCOPES))
        google_calendar_service.events().list(calendarId=WSA_PROD_CALENDAR_ID)
        return google_calendar_service
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_google_calendar_service() -> Resource:
    global google_calendar_service
    return google_calendar_service


GoogleCalendarServiceDependency = Depends(get_google_calendar_service)
