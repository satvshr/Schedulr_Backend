from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport import requests
from django.http import HttpResponse

def auth(request):

    # Load the service account credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS,
        scopes=settings.GOOGLE_CALENDAR_SCOPES
    )

    # Refresh the access token
    request_obj = requests.Request()
    credentials.refresh(request_obj)

    # Get the refreshed access token
    access_token = credentials.token

    # Store the access token in the session
    request.session['access_token'] = access_token

    return HttpResponse('Sucess! your token is: ' + access_token)

