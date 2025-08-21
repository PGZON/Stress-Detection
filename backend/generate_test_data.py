"""
Generate additional stress records for testing the analytics page.
This script will create random stress records for all employees
for the past 14 days to provide enough data for the analytics page.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "stress_sense_db")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    employees_collection = db["employees"]
    devices_collection = db["devices"]
    stress_records_collection = db["stress_records"]
    logger.info(f"Connected to MongoDB: {MONGO_URI}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

def generate_test_records():
    """Generate a large number of test records for analytics"""
    
    employees = list(employees_collection.find())
    if not employees:
        logger.error("No employees found. Please run seed_data.py first.")
        sys.exit(1)
    
    # Get devices for employees
    devices = list(devices_collection.find())
    device_map = {d["employee_id"]: d["device_id"] for d in devices}
    
    if not devices:
        logger.error("No devices found. Please run seed_data.py first.")
        sys.exit(1)
    
    emotions = ["happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"]
    stress_levels = ["Low", "Medium", "High"]
    
    now = datetime.utcnow()
    record_count = 0
    
    # Clear existing records if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        logger.info("Clearing existing stress records...")
        stress_records_collection.delete_many({})
    
    # Create more records per day
    for employee in employees:
        employee_id = employee["employee_id"]
        device_id = device_map.get(employee_id)
        
        if not device_id:
            continue
        
        # Create records for the past 14 days
        for day in range(14):
            # More records per day (5-15)
            for _ in range(random.randint(5, 15)):
                record_date = now - timedelta(days=day)
                
                # Random time during work hours
                hour = random.randint(9, 17)
                minute = random.randint(0, 59)
                record_time = record_date.replace(hour=hour, minute=minute)
                
                # Random emotion with weighted distribution
                emotion_weights = {
                    "happy": 3,
                    "neutral": 5,
                    "sad": 2,
                    "angry": 2,
                    "fear": 1,
                    "disgust": 1,
                    "surprise": 2
                }
                emotion = random.choices(
                    list(emotion_weights.keys()),
                    weights=list(emotion_weights.values()),
                    k=1
                )[0]
                
                # Use realistic mapping
                if emotion in ["happy", "neutral"]:
                    stress_level = "Low"
                elif emotion in ["sad", "surprise"]:
                    stress_level = "Medium"
                else:  # angry, fear, disgust
                    stress_level = "High"
                    
                # Add occasional mismatches
                if random.random() < 0.1:  # 10% chance of mismatch
                    stress_level = random.choice([sl for sl in stress_levels if sl != stress_level])
                
                record_data = {
                    "record_id": str(uuid.uuid4()),
                    "employee_id": employee_id,
                    "device_id": device_id,
                    "emotion": emotion,
                    "stress_level": stress_level,
                    "confidence": random.uniform(40, 95),
                    "timestamp": record_time.isoformat() + "Z",
                    "ingested_at": datetime.utcnow().isoformat() + "Z",
                    "face_quality": {
                        "is_bright": True,
                        "is_proper_size": True,
                        "is_centered": True,
                        "brightness": random.uniform(40, 70),
                        "face_ratio": random.uniform(0.1, 0.3),
                        "center_distance": random.uniform(0.05, 0.2)
                    }
                }
                
                stress_records_collection.insert_one(record_data)
                record_count += 1
                
                # Print progress
                if record_count % 50 == 0:
                    logger.info(f"Created {record_count} stress records so far...")
        
        logger.info(f"Created stress records for employee: {employee['display_name']}")
    
    logger.info(f"Successfully created {record_count} stress records for analytics testing")

if __name__ == "__main__":
    logger.info("Starting test data generation...")
    generate_test_records()
    logger.info("Test data generation completed!")
