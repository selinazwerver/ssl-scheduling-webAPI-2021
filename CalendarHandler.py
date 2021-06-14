from __future__ import print_function
from datetime import datetime, timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class CalendarHandler():
    def __init__(self):
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)

    def field_to_calendar_id(self, field):
        if field == 'A':
            return 'c_k23bjk71b5tqm3od1osjndu5mk@group.calendar.google.com'
        elif field == 'B':
            return 'c_n0qc2fm2otbu5m5kiab8gsefg8@group.calendar.google.com'
        elif field == 'C':
            return 'c_d4igj5ugl0hutsmdnkgaac87ss@group.calendar.google.com'
        elif field == 'D':
            return 'c_c1n27rok56cg74fauicqkma0uc@group.calendar.google.com'

    def write_event_to_calendar(self, teamA, teamB, date, time, field, type, referee='None'):
        startTime = date + 'T' + time + ':00-00:00'
        endTime = datetime.strftime(datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S%z') + timedelta(hours=1),
                                    '%Y-%m-%dT%H:%M:%S%z')

        if type == 'friendly':
            title = 'Friendly Match %s - %s' % (teamA, teamB)
        elif type == 'match':
            title = '%s - %s' % (teamA, teamB)
        else:
            return

        event = {
            'summary': title,
            'location': field,
            'description': 'Referees: ' + referee,
            'start': {
                'dateTime': startTime,
                'timeZone': 'Iceland',
            },
            'end': {
                'dateTime': endTime,
                'timeZone': 'Iceland',
            },
        }

        self.service.events().insert(calendarId=self.field_to_calendar_id(field), body=event).execute()
