from flask import Blueprint, request
from flask import Blueprint, redirect, url_for, request, session, jsonify
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

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

