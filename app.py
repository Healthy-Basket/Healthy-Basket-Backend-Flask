from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
#from extensions import mongo
from flask_pymongo import PyMongo


from config import config_by_name

load_dotenv()

mongo = PyMongo() 

def create_app():
    """creates main app"""
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_object(config_by_name["prod"])
    CORS(app, supports_credentials=True)
    
    from home import home
    from auth import auth
    from fitbit import fitbit
    from onboarding import onboarding
    from googlefit2 import googlefit
    with app.app_context():
        #mongo = PyMongo(app)
        #print("MONGO_URI:", app.config.get("MONGO_URI"))
        mongo.init_app(app)
        print("Mongo initialized:", mongo.db)
        app.register_blueprint(home)
        app.register_blueprint(auth)
        app.register_blueprint(fitbit)
        app.register_blueprint(googlefit)
        app.register_blueprint(onboarding)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)