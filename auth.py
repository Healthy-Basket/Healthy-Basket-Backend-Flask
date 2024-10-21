from flask import Blueprint, request
from flask import Blueprint, redirect, url_for, request, session, jsonify
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import requests
from app import mongo

auth = Blueprint('auth', __name__)
load_dotenv()
client_id  = os.getenv("CLIENT_ID")
client_secret  = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
authorization_uri = os.getenv("FITBIT_AUTHORIZATION_URI")
token_url = os.getenv("TOKEN_REQUEST_URI")
# OAuth2 session
# Define the scopes for the OAuth2 session
scopes = ['activity', 'sleep', 'weight','profile', 'nutrition', 'heartrate', 'location']
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

@auth.route('/authorize')
def authorize():
    url = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23PW6R&redirect_uri=http%3A%2F%2Flocalhost&scope=activity%20nutrition%20heartrate%20location'
    authorization_url, state = oauth.authorization_url(authorization_uri)
    session['oauth_state'] = state
    #return jsonify({"msg":state,"msg2": authorization_url})
    return redirect(authorization_url)

@auth.route('/callback')
def callback():
    try:
        oauth_state = session.get('oauth_state')
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, state=oauth_state)
        print(f"Request URL: {request.url}")  # Log the request URL
        
        # Fetch the token
        token = oauth.fetch_token(
            token_url,
            authorization_response=request.url,
            auth=HTTPBasicAuth(client_id, client_secret)
        )
        session['token'] = token
        # Save token and return a success message
        return jsonify({"message": "Authentication successful", "token": token})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 400
    

@auth.route('/profile')
def profile():
    # Retrieve the token from the session
    token = session.get("token")
    
    # Ensure the token is present before making the request
    if not token:
        return jsonify({"error": "Token is missing. Please authorize again."}), 401
    
    access_token = token.get("access_token")
    profile_url = "https://api.fitbit.com/1/user/-/profile.json"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Make a GET request to the Fitbit API for the user's profile
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx

        # Parse the JSON response from the API
        profile_data = response.json().get('user', {})
        
        # Extract desired fields
        fullname = profile_data.get('fullName')
        gender = profile_data.get('gender')
        age = profile_data.get('age')  # Fitbit might not directly provide age; you might need to calculate it using the birthdate.
        weight = profile_data.get('weight')  # Weight might be in a different API endpoint, so adjust if needed.
        height = profile_data.get('height')
        sleepTracking = profile_data.get('sleepTracking')

        # Construct the document to insert into MongoDB
        user_profile = {
            "fullName": fullname,
            "gender": gender,
            "age": age,
            "weight": weight,
            "height": height,
            "sleepTracking": sleepTracking,
            "fitbit_id": profile_data.get('encodedId')  # Store the Fitbit user ID for reference
        }
        
        # Upsert into MongoDB (insert or update if the record exists)
        # Assuming you use `fitbit_id` as a unique identifier for the user
        mongo.db.user_profiles.update_one(
            {"fitbit_id": profile_data.get('encodedId')},
            {"$set": user_profile},
            upsert=True
        )
        
        return jsonify({"message": "Profile data saved successfully", "profile": user_profile}), 200

    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors (like 401 for unauthorized)
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), response.status_code
    except requests.exceptions.RequestException as req_err:
        # Handle any other request errors
        return jsonify({"error": f"Request error: {req_err}"}), 500
    except Exception as e:
        # General error handling
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    
