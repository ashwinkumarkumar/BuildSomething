# app/simulator.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import random

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.gearbox

VALID_SENSORS = ["sensor1", "sensor2", "sensor3", "sensor4"]
VALID_LOADS = [0, 30, 60, 90]

def get_signal(label, sensor_count):
    """
    Returns vibration signals for given label and sensor count as list of floats.
    """
    collection_name = f"test_signals_{label.lower()}"

    # Query MongoDB collection
    collection = db[collection_name]
    doc = collection.aggregate([{"$sample": {"size": 1}}]).next()

    if not doc:
        raise ValueError(f"No data found in collection '{collection_name}'")

    # Return sensors as list of floats
    sensors = doc["sensors"]
    return sensors[:sensor_count] if sensor_count <= len(sensors) else sensors
