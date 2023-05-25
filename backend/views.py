from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport import requests
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
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

    return redirect('get')

@csrf_exempt
def api(request):
    if request.method == 'POST':
        service = build("calendar", "v3", credentials=credentials)
        event_data = json.loads(request.body.decode('utf-8'))
        event_list = event_data if isinstance(event_data, list) else []
        calendar_id = settings.GOOGLE_CALENDAR_ID

        for event in event_list:
            event_id = event.get("id")
            event_summary = event.get("title")
            event_description = event.get("description")
            start_time = datetime.fromtimestamp(event.get("day", 0) / 1000.0)
            end_time = start_time + timedelta(days=1)
            event_color_id = event.get("colorId")
                # Create a new event
            service.events().insert(
                calendarId=calendar_id,
                body={
                    "summary": event_summary,
                    "description": event_description,
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

        return HttpResponse('Event update/creation/deletion completed successfully!', headers={'Access-Control-Allow-Origin': 'http://localhost:3000'})

@csrf_exempt
def deletion(request):
    if request.method == 'POST':
        service = build("calendar", "v3", credentials=credentials)
        event_data = json.loads(request.body.decode('utf-8'))
        print(event_data)
        event_list = event_data if isinstance(event_data, list) else []
        calendar_id = settings.GOOGLE_CALENDAR_ID

        for event in event_list:
            event_summary = event.get("title")
            start_time = datetime.fromtimestamp(event.get("day", 0) / 1000.0)

            events = service.events().list(calendarId=calendar_id, q=event_summary).execute()
            print(events)
            items = events.get('items', [])
            print(items)
            print("HEL")
            for it in items:
                # if it['start'].get('dateTime') == start_time.isoformat():
                    event_id = it['id']
                    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
                    print("HELLLOOOO")
                
        return HttpResponse("Deleted!")

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
    event_data = []
    color_map = {
        "1" : "green",
        "2": "blue",
        "11" : "red"
    }
    for event in event_list:
        date_time_string = event.get('start').get('dateTime')
        date_time_obj = datetime.fromisoformat(date_time_string.replace("Z", "+00:00"))
        utc_time = date_time_obj.astimezone(timezone.utc)
        milliseconds = int(utc_time.timestamp() * 1000)
        color_id = event.get('colorId')
        data = {
            'title' : event.get('summary'),
            'description' : event.get('description'),
            'colorId' : color_id,
            'day': milliseconds,
            'id' : event.get('id'),
            'label' : color_map.get(color_id)
        }
        event_data.append(data)
    
    return JsonResponse(event_data, safe=False)

            # event_id = event['id']
            # event_summary = event['summary']
            # event_description = event.get('description', '')
            # event_color_id = event.get('colorId', '')