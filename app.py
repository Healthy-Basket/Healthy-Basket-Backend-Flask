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
    from onboarding import onboarding
    from fitbit import fitbit

    with app.app_context():
        #mongo = PyMongo(app)
        mongo.init_app(app)
        app.register_blueprint(home)
        app.register_blueprint(auth)
        app.register_blueprint(fitbit)
        app.register_blueprint(onboarding)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)