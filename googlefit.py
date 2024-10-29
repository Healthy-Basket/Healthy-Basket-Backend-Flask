from flask import Blueprint, request, session, redirect, jsonify
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


googlefit = Blueprint('googlefit', __name__)


# OAuth 2.0 credentials
CLIENT_ID = os.getenv('CLIENT_ID1')
CLIENT_SECRET = os.getenv('CLIENT_SECRET1')
REDIRECT_URI = os.getenv('REDIRECT_URI1')

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

# Home route
@googlefit.route('/googlefit')
def home():
    return "<h1>Welcome to the Healthy Basket API</h1><a href='/auth'>Authenticate with Google Fit</a>"

@googlefit.route('/auth')
def auth():
    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    print(f"Redirect URI being used: {REDIRECT_URI}")
    authorization_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(authorization_url)

# OAuth2 callback
@googlefit.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES, state=state,
        redirect_uri=REDIRECT_URI
    )
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    
    # Debugging: Print credentials
    print(session['credentials'])
    
    return redirect('/googleProfile')

@googlefit.route('/googleProfile')
def profile():
    if 'credentials' not in session:
        return redirect('/auth')
    
    credentials = Credentials(**session['credentials'])
    fitness_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    data_sources = fitness_service.users().dataSources().list(userId='me').execute()
    return jsonify(data_sources)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    googlefit.config['SESSION_PERMANENT'] = False
    googlefit.config['SESSION_TYPE'] = 'filesystem'
    googlefit.run(debug=True)
