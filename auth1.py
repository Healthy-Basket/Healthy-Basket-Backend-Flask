from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import re

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()
jwt = JWTManager()

# Mock database for storing users
mock_db = {}

# Initialize JWT with app
def init_jwt(app):
    jwt.init_app(app)

# Helper function to validate email
def is_valid_email(email):
    return re.match(r'[^@]+@[^@]+\.[^@]+', email)

### Email and Password Signup
@auth.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email) or len(password) < 6:
        return jsonify({"msg": "Invalid email or password length."}), 400

    if email in mock_db:
        return jsonify({"msg": "Email already exists."}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    mock_db[email] = {"password": hashed_pw}

    return jsonify({"msg": "User created successfully."}), 201

### Email and Password Login
@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = mock_db.get(email)
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"msg": "Invalid credentials."}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200

### Google OAuth Signup/Login
@auth.route('/google-signup', methods=['POST'])
def google_signup():
    token = request.json.get("token")
    if not token:
        return jsonify({"msg": "Token missing"}), 400

    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        email = id_info.get("email")
        if not email:
            return jsonify({"msg": "Google account email not found."}), 400

        if email not in mock_db:
            mock_db[email] = {"password": None}  # Set up user without password

        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token), 200

    except ValueError:
        return jsonify({"msg": "Invalid token"}), 400

# Protect routes that require a valid token with @jwt_required()
@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
