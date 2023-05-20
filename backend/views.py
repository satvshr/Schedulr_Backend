from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport import requests
from django.http import HttpResponse
from googleapiclient.discovery import build

# Load the service account credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_CREDENTIALS,
    scopes=settings.GOOGLE_CALENDAR_SCOPES
)
event_dict = {}
def auth(request):
    # Refresh the access token
    request_obj = requests.Request()
    credentials.refresh(request_obj)

    # Get the refreshed access token
    access_token = credentials.token

    # Store the access token in the session
    request.session['access_token'] = access_token

    return HttpResponse('Sucess! your token is: ' + access_token)

def api(request):
    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=credentials)
    event_data = request.POST
    event_id = event_data.get('event_id')
    # Create the event object
    event = {
        'summary': 'garble',
        'start': {
            'dateTime': '2023-05-20T1:00:00',
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': '2023-05-20T2:00:00',
            'timeZone': 'Asia/Kolkata',
        },
    }

    # Insert the event into the calendar
    calendar_id = settings.GOOGLE_CALENDAR_ID 
    if event_id:
        event_dict.pop(event_data.get('summary'))
        created_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        event_id = created_event['id']
        event_dict[created_event['summary']] = event_id        
        return HttpResponse('Event updated successfully!')
    else:
        # Create a new event
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        event_id = created_event['id']
        event_dict[created_event['summary']] = event_id
        return HttpResponse('Event created successfully!')

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

def delete_event(request):
    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=credentials)
    event_data = request.POST
    event_id = event_data.get('event_id')
    # Insert the event into the calendar
    calendar_id = settings.GOOGLE_CALENDAR_ID  # Use 'primary' for the primary calendar
    response = service.events().remove(calendarId=calendar_id, eventId = event_id).execute()
    event_dict.pop(response['summary'])
    # Return a response indicating the success
    return HttpResponse("Sucessfull!")