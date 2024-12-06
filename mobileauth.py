from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from google_auth_oauthlib.flow import Flow
import os
import requests

auth = Blueprint('auth', __name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("client_id")
GOOGLE_CLIENT_SECRET = os.getenv("client_secret")
GOOGLE_REDIRECT_URI = os.getenv("redirect_uri")
SCOPES = ["openid","https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]

# Helper function to generate a MongoDB-safe user dictionary
def create_user(email, password_hash=None, google_id=None):
    return {
        "email": email,
        "password_hash": password_hash,
        "google_id": google_id
    }

# Generate the authorization URL with PKCE
@auth.route('/google_signup')
def google_signup():
    flow = Flow.from_client_secrets_file(
        'authclient_secret.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        prompt='consent',
        include_granted_scopes='true',
        code_challenge_method='S256'
    )
    session['state'] = state
    return jsonify({"authorization_url": authorization_url})

# Google OAuth callback for mobile
@auth.route('/google_callback')
def google_callback():
    state = request.args.get('state')
    if state != session.get('state'):
        return jsonify({"error": "State mismatch"}), 400

    flow = Flow.from_client_secrets_file(
        'authclient_secret.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    user_info = user_info_response.json()

    email = user_info['email']
    google_id = user_info['sub']

    # Save user or retrieve existing user
    user = mongo.db.users.find_one({"google_id": google_id})
    if not user:
        user = create_user(email, google_id=google_id)
        mongo.db.users.insert_one(user)

    # Return token for mobile app
    session.pop('state', None)
    return jsonify({"access_token": credentials.token, "user_id": str(user['_id'])}), 200
