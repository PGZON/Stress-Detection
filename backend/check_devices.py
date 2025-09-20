import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017/')
DB_NAME = os.getenv('DB_NAME', 'stress_sense_db')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
devices_collection = db['devices']

print('Devices in database:')
for device in devices_collection.find({}, {'_id': 0}):
    print(f'  Device ID: {device.get("device_id")}')
    print(f'  Employee ID: {device.get("employee_id")}')
    print(f'  API Key Hash: {device.get("api_key_hash")[:10] if device.get("api_key_hash") else "None"}...')
    print(f'  Active: {device.get("active")}')
    print()