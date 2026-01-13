import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config.settings import get_config

cfg = get_config()
SERVICE_ACCOUNT_FILE = cfg["SERVICE_ACCOUNT_FILE"]

def get_calendar_service():
    """Authenticates and returns the Google Calendar service object."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"⚠️ Warning: Service account file not found at {SERVICE_ACCOUNT_FILE}")
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"⚠️ Error creating calendar service: {e}")
        return None

def create_calendar_event(summary, start_time, end_time, description=""):
    """
    Creates an event in the primary Google Calendar.
    Args:
        summary (str): Title of the event.
        start_time (str): ISO format timestamp (e.g., '2023-10-01T10:00:00').
        end_time (str): ISO format timestamp.
        description (str): Optional notes.
    """
    service = get_calendar_service()
    if not service:
        return {"success": False, "error": "Calendar service unavailable"}

    try:
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'Europe/Stockholm'},
            'end': {'dateTime': end_time, 'timeZone': 'Europe/Stockholm'},
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return {"success": True, "link": created_event.get('htmlLink')}
    except Exception as e:
        return {"success": False, "error": str(e)}
