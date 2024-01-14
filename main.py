import os.path
from oura import getSleepEvents
import json
from datetime import datetime, timedelta, timezone
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# * Control Vars + Config
HISTORY_MODE = False            # Get all events from historic_start
historic_start = "2022-12-20"
CLEAR = False                   # Clear calendar before adding events


DEBUG = False
# * End of Config



if HISTORY_MODE:
    range_start = historic_start = "2022-12-20"
else: # CRON MODE
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    range_start = yesterday.strftime("%Y-%m-%d")


SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/calendar.events"]

with open("secrets.json") as f:
    secrets = json.load(f)
calendar_ID = secrets["calendar_ID"]


def getEvents(creds):
    """Gets all events from the calendar.
    """
    try:
        service = build("calendar", "v3", credentials=creds)

        events_result = (
            service.events()
            .list(
                calendarId=calendar_ID,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return
        return events

    except HttpError as error:
        print(f"An error occurred: {error}")

def getRecentEvents(creds):
    """Gets all events from the calendar.
    """
    try:
        service = build("calendar", "v3", credentials=creds)

        yesterday_formatted = (today - timedelta(days=2)).isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId=calendar_ID,
                timeMin=yesterday_formatted,
                # maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return
        return events

    except HttpError as error:
        print(f"An error occurred: {error}")

def addEvent(creds, e):
    """Adds an event to the calendar.
    """
    try:
        service = build("calendar", "v3", credentials=creds)
    
        event = service.events().insert(calendarId=calendar_ID, body=e).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print(f"An error occurred: {error}")

def checkEventExists(preexisting, e):
    """Checks if an event already exists in the calendar.
    """
    if e["summary"] in [event["summary"] for event in preexisting]:
        # print("same name found")
        
        # find the event with the same name
        for event in preexisting:
            if event["summary"] == e["summary"]:
                # print("same name identified")

                # Parse event datetimes
                start_datetime = datetime.fromisoformat(event["start"]["dateTime"])
                end_datetime = datetime.fromisoformat(event["end"]["dateTime"])

                # Parse e datetimes (re add timezone)
                e_start_datetime = datetime.fromisoformat(e["start"]["dateTime"] +  e["start"]["timeZone"][3:])
                e_end_datetime = datetime.fromisoformat(e["end"]["dateTime"] +  e["end"]["timeZone"][3:])


                # print(start_datetime, e_start_datetime)
                # print(end_datetime, e_end_datetime)
                
                if start_datetime == e_start_datetime and end_datetime == e_end_datetime:
                    return True

    return False

    

def main():
    """ Main function: Gets sleep data from Oura, then adds it to Google Calendar.
    """

    # * Google Calendar API

    # Auth + Build Service
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    
    


    # * Get all events
    if HISTORY_MODE:
        preexisting = getEvents(creds) #! this caps out at 250 by default
    else:
        preexisting = getRecentEvents(creds)
    if preexisting:
        if DEBUG: print("Received preexisting events...", len(preexisting))


    if CLEAR:
        service = build("calendar", "v3", credentials=creds)
        print("Clearing calendar...")
        for event in preexisting:
            # print("\t", event["summary"])

            # Delete the event
            if CLEAR:
                print("\t\tDeleting event...")
                service.events().delete(calendarId=calendar_ID, eventId=event["id"]).execute()


    # * Get sleep data
    if DEBUG: print("Getting sleep data... for", range_start)
    events = getSleepEvents(range_start)
    if DEBUG: print("Received", len(events), "sleep blocks")


    # * Add events
    for e in events:
        if DEBUG: print("\t", e["summary"])

        # check if event already exists
        if checkEventExists(preexisting, e):
            if DEBUG: print("\t\tEvent already exists")
            continue

        print("\t\tAdding event...")
        print("\t\t", e["start"]["dateTime"], e["summary"])
        addEvent(creds, e)
     


if __name__ == "__main__":
  main()