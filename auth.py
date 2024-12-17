from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from app import mongo
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import requests

auth = Blueprint('auth', __name__)

# Google OAuth configuration
IOS_GOOGLE_CLIENT_ID = os.getenv("IOS_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_ID = os.getenv("client_id")
GOOGLE_CLIENT_SECRET = os.getenv("client_secret")
GOOGLE_REDIRECT_URI = os.getenv("redirect_uri")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email"
    ]

# Helper function to generate a MongoDB-safe user dictionary
def create_user(email,firstname,lastname, password_hash=None, google_id=None):
    return {
        "email": email,
        "password_hash": password_hash,
        "google_id": google_id,
        "firstname": firstname,
        "lastname": lastname
    }

# Signup with email and password
@auth.route('/signup', methods=['POST'])
def signup():
    #payload data
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get("name")

    #name validation
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Split the full name into first and last names
    name_parts = name.split()
    if len(name_parts) < 2:
        return jsonify({"error": "Full name must include first and last names"}), 400

    firstname = name_parts[0]
    lastname = ' '.join(name_parts[1:])
    

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    password_hash = generate_password_hash(password)
    user = create_user(email,firstname,lastname, password_hash=password_hash)
    mongo.db.users.insert_one(user)
    
    # create a user object here so that i can grab the uid and use it to fetch the user's data
    user_object = {
        "id": str(user['_id']),
        "email": user['email'],
        "name": "{} {}".format(firstname,lastname)
    }

    return jsonify({
        "message": "User registered successfully",
        "user": user_object
        }), 201

# Login with email and password
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # return specific error messages 
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email})
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid email or password"}), 401

    
    #create access token jwt
    access_token = create_access_token(identity=str(user['_id']))

    # create a user object here so that i can grab the uid and use it to fetch the user's data
    user_object = {
        "id": str(user['_id']),
        "email": user['email'],
        "name": "{} {}".format(user.get('firstname'),user.get('lastname'))
    }
    return jsonify( {
        "message": "Logged in successfully",
        "access_token": access_token,
        "user": user_object
    }), 200

# Initiate Google Sign-In over the web
@auth.route('/google_signup')
def google_signup():
    flow = Flow.from_client_secrets_file(
        'authclient_secret.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

# Google OAuth callback
@auth.route('/google_callback')
def google_callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'authclient_secret.json', scopes=SCOPES, state=state,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    user_info_response = requests.get(
        "https://people.googleapis.com/v1/people/me?personFields=emailAddresses,names",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    user_info = user_info_response.json()
    email = user_info['emailAddresses'][0]['value']
    google_id = user_info['resourceName']

    # Extract first name and last name
    firstname = ""
    lastname = ""
    if 'names' in user_info:
        names = user_info['names']
        if names:
            firstname = names[0].get('givenName', '')
            lastname = names[0].get('familyName', '')

    user = mongo.db.users.find_one({"google_id": google_id})
    if not user:
        user = create_user(email, firstname, lastname, google_id=google_id)
        mongo.db.users.insert_one(user)

    access_token = create_access_token(identity=str(user['_id']))
    # create a user object here so that i can grab the uid and use it to fetch the user's data
    user_object = {
        "id": str(user['_id']),
        "email": user['email'],
        "name": "{} {}".format(firstname,lastname)
    }

    return jsonify({
        "message": "Google sign-up successful",
        "access_token": access_token,
        "user": user_object
    }), 200

@auth.route('/mobile_google_signup', methods=['POST'])
def mobile_google_signup():
    data = request.get_json()
    id_token_str = data.get('id_token')

    try:
        # Create a requests.Session object
        session = requests.Session()
        # Create a requests.Request object
        req = requests.Request(method="GET")
        # Prepare the request
        prepped = session.prepare_request(req)
        # Verify the ID token
        id_info = id_token.verify_oauth2_token(id_token_str, prepped, IOS_GOOGLE_CLIENT_ID)
        
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = id_info['email']
        google_id = id_info['sub']
        firstname = id_info.get('given_name', '')
        lastname = id_info.get('family_name', '')

        user = mongo.db.users.find_one({"google_id": google_id})
        if not user:
            user = create_user(email, firstname, lastname, google_id=google_id)
            mongo.db.users.insert_one(user)

        access_token = create_access_token(identity=str(user['_id']))
        user_object = {
            "id": str(user['_id']),
            "email": user['email'],
            "name": "{} {}".format(firstname, lastname)
        }

        return jsonify({
            "message": "Google sign-up successful",
            "access_token": access_token,
            "user": user_object
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid ID token"}), 400

# Logout endpoint
@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200
