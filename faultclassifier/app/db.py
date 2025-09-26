import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.gearbox
