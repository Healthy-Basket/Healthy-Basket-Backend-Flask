import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    #JWT_SECRET_KEY = os.getenv("MY_JWT_SECRET")
    #JWT_ACCESS_TOKEN_EXPIRES = False
    

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    #JWT_SECRET_KEY = os.getenv("MY_JWT_SECRET")
    #JWT_ACCESS_TOKEN_EXPIRES = False
   
    

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
    )