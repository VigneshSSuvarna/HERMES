import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class HermesCalendar:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        print("[Calendar Engine]: Initializing Google Calendar Sync...")
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"[Calendar Error]: Failed to refresh token: {e}")
                    self.creds = None
            
            if not self.creds:
                if not os.path.exists('credentials.json'):
                    print("[Calendar Error]: credentials.json not found in root directory!")
                    return
                # Spins up a local web server to ask for your permission
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0, timeout_seconds=300)
            
            # Save the credentials for the next run so you only have to log in once
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            print("[Calendar Engine]: Successfully connected to Google Calendar.")
        except Exception as e:
            print(f"[Calendar Error]: Failed to build service: {e}")

    def get_upcoming_events(self, max_results=5) -> str:
        """Fetches the next few upcoming events from the user's calendar."""
        if not self.service:
            return "Calendar service is offline or unauthenticated."
        
        try:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                return "You have no upcoming meetings or events scheduled, Sir."

            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Parse the time to make it readable for the AI
                if 'T' in start:
                    time_obj = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_time = time_obj.strftime("%I:%M %p on %b %d")
                else:
                    # All-day event
                    time_obj = datetime.datetime.strptime(start, "%Y-%m-%d")
                    formatted_time = time_obj.strftime("All day on %b %d")

                event_list.append(f"- {event['summary']} at {formatted_time}")
            
            joined_events = "\n".join(event_list)
            return f"Here are your upcoming scheduled events:\n{joined_events}"

        except Exception as e:
            return f"Failed to retrieve calendar events: {e}"