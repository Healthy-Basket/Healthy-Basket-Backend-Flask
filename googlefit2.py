from flask import Blueprint, request, session, redirect, jsonify
import os
import requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from app import mongo

load_dotenv()


googlefit = Blueprint('googlefit', __name__)


# OAuth 2.0 credentials
CLIENT_ID = os.getenv('CLIENT_ID1')
CLIENT_SECRET = os.getenv('CLIENT_SECRET1')
REDIRECT_URI = os.getenv('REDIRECT_URI1')

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

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
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES, state=state,
        redirect_uri=REDIRECT_URI
    )
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    # Fetch the user's Google Account ID using the Google People API
    people_api_url = "https://people.googleapis.com/v1/people/me"
    response = requests.get(people_api_url, headers={"Authorization": f"Bearer {credentials.token}"})
    
    # If the response is successful, store the user ID in the session
    if response.status_code == 200:
        user_data = response.json()
        google_account_id = user_data.get('resourceName', None)
        
        # Store the Google Account ID in the session if found
        if google_account_id:
            session['google_account_id'] = google_account_id
            print(f"User Google Account ID: {google_account_id}")
        else:
            print("Error: Google Account ID not found.")
    
    else:
        print(f"Error fetching user info: {response.status_code} - {response.text}")

    
    # Debugging: Print credentials
    print(credentials)
    print(session['credentials'])
    for i in session:
        print(i)
    
    return redirect('/user_health_summary')


# URL for Google Fit data aggregation endpoint
GOOGLE_FIT_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

def get_google_fit_data(credentials, data_type_name, start_time, end_time):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    # Set up request payload
    body = {
        "aggregateBy": [{"dataTypeName": data_type_name}],
        "bucketByTime": {"durationMillis": 86400000},  # Daily data
        "startTimeMillis": int(start_time.timestamp() * 1000),
        "endTimeMillis": int(end_time.timestamp() * 1000),
    }
    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()

@googlefit.route("/user_health_summary", methods=["GET"])
def user_health_summary():
    if 'credentials' not in session:
        return redirect('/auth')  # Redirect to authentication if not logged in
    
    # Initialize credentials and set up time range (last 7 days)
    credentials = Credentials(**session['credentials'])
    end_time = datetime.now()
    start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)  # Start of the day

    
    # Retrieve and process required data
    try:
        # Active minutes
        active_minutes_data = get_google_fit_data(credentials, "com.google.active_minutes", start_time, end_time)
        
        # Heart minutes
        heart_minutes_data = get_google_fit_data(credentials, "com.google.heart_minutes", start_time, end_time)
        
        # Calories expended
        calories_data = get_google_fit_data(credentials, "com.google.calories.expended", start_time, end_time)
        
        # Sleep data (if available)
        sleep_data = get_google_fit_data(credentials, "com.google.sleep.segment", start_time, end_time)
        
        # Body weight (optional if recorded in Google Fit)
        weight_data = get_google_fit_data(credentials, "com.google.weight", start_time, end_time)
    
        # Processing data into a refined structure
        refined_data = {
            "activity": {
                "active_minutes": sum(bucket['dataset'][0]['point'][0]['value'][0]['intVal']
                                      for bucket in active_minutes_data.get('bucket', []) if bucket['dataset'][0]['point']),
                "heart_minutes": sum(bucket['dataset'][0]['point'][0]['value'][0]['fpVal']
                                     for bucket in heart_minutes_data.get('bucket', []) if bucket['dataset'][0]['point']),
            },
            "calories_burned": sum(bucket['dataset'][0]['point'][0]['value'][0]['fpVal']
                                   for bucket in calories_data.get('bucket', []) if bucket['dataset'][0]['point']),
            "sleep": {
                "total_sleep_duration": sum((int(bucket['endTimeMillis']) - int(bucket['startTimeMillis']))
                                            for bucket in sleep_data.get('bucket', []) if bucket['dataset'][0]['point']) / (1000 * 60 * 60),  # in hours
            },
            "body_metrics": {
                "weight": weight_data['bucket'][0]['dataset'][0]['point'][0]['value'][0]['fpVal']
                          if weight_data.get('bucket') and weight_data['bucket'][0]['dataset'][0]['point'] else "Not available"
            }
        }

        # Upsert into MongoDB using a unique identifier for each user
        # `user_id` here is a custom identifier you assign to each user upon authentication
        user_id = session.get('google_account_id')  # Fetching user_id from session data

        if user_id:
            mongo.db.user_profiles.update_one(
                {"user_id": user_id},  # Use your unique identifier
                {"$set": refined_data},
                upsert=True
            )
        else:
            return jsonify({"error": "User ID not found in session"}), 400
          
        return jsonify(refined_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    googlefit.config['SESSION_PERMANENT'] = False
    googlefit.config['SESSION_TYPE'] = 'filesystem'
    googlefit.run(debug=True)
