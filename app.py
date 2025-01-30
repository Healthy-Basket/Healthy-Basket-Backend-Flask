from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
#from extensions import mongo
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager


from config import config_by_name

load_dotenv()

mongo = PyMongo()
jwt = JWTManager() 

def create_app():
    """creates main app"""
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_object(config_by_name["prod"])
    app.config['MONGO_URI'] = os.getenv("MONGO_URI")
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    print("🔍 MONGO_URI:", app.config['MONGO_URI']) 

    if not app.config['MONGO_URI']:
        raise ValueError("❌ MONGO_URI is not set! Check your environment variables.")


    CORS(app, supports_credentials=True)


    from home import home
    from auth import auth
    from fitbit import fitbit
    from onboarding import onboarding
    from googlefit2 import googlefit
    with app.app_context():
        #mongo = PyMongo(app)
        print("MONGO_URI:", app.config.get("MONGO_URI"))
        mongo.init_app(app)
        jwt.init_app(app)
        print("Mongo initialized:", mongo.db)
        app.register_blueprint(home, url_prefix='/api/v1')
        app.register_blueprint(auth, url_prefix='/api/v1/auth')
        app.register_blueprint(fitbit)
        app.register_blueprint(googlefit)
        app.register_blueprint(onboarding)
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)