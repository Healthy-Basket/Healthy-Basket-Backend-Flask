
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://bernard:YQHF6XoJx8EJ7iId@master.rabgt.mongodb.net/?retryWrites=true&w=majority&appName=master"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    collections = mongo.HealthyBasket.list_collection_names()
    print({'collections': collections})
except Exception as e:
    print(e)