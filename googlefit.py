from flask import Blueprint, request, session, redirect, jsonify,url_for
import os
import requests
from datetime import datetime, timedelta
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
GOOGLE_FIT_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

# Helper function to convert credentials to dictionary
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

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
    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES,
        state=session['state'], redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    session['credentials'] = credentials_to_dict(flow.credentials)
    return redirect(url_for('googlefit.profile'))

# Helper function to get Google Fit service
def get_google_fit_service():
    credentials = Credentials(**session['credentials'])
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# Helper function to request specific Google Fit data
def fetch_metric_data(data_type_name, start_time, end_time):
    access_token = session['credentials']['token']
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    body = {
        "aggregateBy": [{"dataTypeName": data_type_name}],
        "bucketByTime": {"durationMillis": 86400000},  # Daily data in milliseconds
        "startTimeMillis": int(start_time.timestamp() * 1000),
        "endTimeMillis": int(end_time.timestamp() * 1000),
    }
    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()

# Profile endpoint to gather and return specific data
@googlefit.route('/googleProfile')
def profile():
    if 'credentials' not in session:
        return redirect(url_for('googlefit.oauth2callback'))
    
    # Define the time range (e.g., last 7 days)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # Fetch specific metrics
    active_minutes = fetch_metric_data("com.google.active_minutes", start_time, end_time)
    calories_expended = fetch_metric_data("com.google.calories.expended", start_time, end_time)
    heart_minutes = fetch_metric_data("com.google.heart_minutes", start_time, end_time)
    
    # Organize data into a structured response
    health_data = {
        "active_minutes": active_minutes,
        "calories_expended": calories_expended,
        "heart_minutes": heart_minutes
    }
    
    return jsonify(health_data)
