from flask import Blueprint, request, jsonify
#from extensions import mongo
from app import mongo

home = Blueprint('home', __name__, url_prefix='/api/v1')

@home.route('/', methods=['GET', 'POST'])
def home_view():
    return jsonify({"msg":"welcome to healthy Basket"}),200

@home.route('/saveuser', methods=['POST'])
def save_user():
    # Get user data from the request
    user_data = request.get_json()
    
    # Basic validation
    if not user_data or not 'username' in user_data or not 'email' in user_data:
        return jsonify({"error": "Invalid input"}), 400
    
    # Create a new user document
    user = {
        "username": user_data['username'],
        "email": user_data['email'],
        # You can add more fields as needed
    }

    # Insert the user into the MongoDB collection
    try:
        mongo.cx["HealthyBasket"].users.insert_one(user)  # Assuming you have a 'users' collection
        return jsonify({"msg": "User saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@home.route('/list_collections')
def list_collections():
    collections = mongo.db.list_collection_names()
    return {'collections': collections}
    