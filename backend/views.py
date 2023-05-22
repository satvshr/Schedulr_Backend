from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json

# Load the service account credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_CREDENTIALS,
    scopes=settings.GOOGLE_CALENDAR_SCOPES
)

@csrf_exempt
def auth(request):
    # Refresh the access token
    request_obj = requests.Request()
    credentials.refresh(request_obj)

    # Get the refreshed access token
    access_token = credentials.token

    # Store the access token in the session
    request.session['access_token'] = access_token

    return redirect('api')

@csrf_exempt
def api(request):
    while request.method == 'POST':
        service = build("calendar", "v3", credentials=credentials)
        event_data = json.loads(request.body.decode('utf-8'))
        print(event_data)
        # Get the list of events from the payload
        event_list = event_data if isinstance(event_data, list) else []
        print(event_list)
        calendar_id = settings.GOOGLE_CALENDAR_ID

        for event in event_list:
            event_id = event.get("id")
            event_summary = event.get("title")
            event_description = event.get("description")
            start_time = datetime.fromtimestamp(event.get("day", 0) / 1000.0)
            end_time = start_time + timedelta(days=1)
            event_color_id = event.get("colorId")
            print(event_summary)
            print(event_description)
            print(start_time)
            print(end_time)
            print(event_color_id)
            if event_id:
                # Update an event
                service.events().update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body={
                        "summary": event_summary,
                        "start": {
                            "dateTime": start_time.isoformat()
                        },
                        "end": {
                            "dateTime": end_time.isoformat()
                        },
                        "colorId": event_color_id
                    }
                ).execute()
            else:
                # Create a new event
                service.events().insert(
                    calendarId=calendar_id,
                    body={
                        "summary": event_summary,
                        "start": {
                            "dateTime": start_time.isoformat(),
                            "timeZone": "Asia/Kolkata" 
                        },
                        "end": {
                            "dateTime": end_time.isoformat(),
                            "timeZone": "Asia/Kolkata" 

                        },
                        "colorId": event_color_id
                    }
                ).execute()

        return HttpResponse('Event update/creation completed successfully!', headers={'Access-Control-Allow-Origin': 'http://localhost:3000'})


@csrf_exempt
def get_events(request):
    access_token = request.session.get('access_token')

    credentials.token = access_token
    service = build('calendar', 'v3', credentials=credentials)

    # Call the API to retrieve events
    calendar_id = settings.GOOGLE_CALENDAR_ID  # Use 'primary' for the primary calendar
    events = service.events().list(calendarId=calendar_id).execute()

    # Process the list of events
    event_list = events.get('items', [])
    for event in event_list:
        summary = event.get('summary', 'No summary')
        start_time = event.get('start', {}).get('dateTime', 'No start time')
        # end_time = event.get('end', {}).get('dateTime', 'No end time')
        print(f"Summary: {summary}")
        print(f"Start Time: {start_time}")
        print("-----------------------")
    return HttpResponse("okie")
