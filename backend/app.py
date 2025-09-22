# uvicorn app:app --reload
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
# from deepface import DeepFace  # Removed - using custom CNN model instead
import io
from typing import Dict, List
import json
from datetime import datetime
import os
from pydantic import BaseModel
import base64
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from app.models.stress_analysis import analyze_image
from app.models.models import get_all_stress_records

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StressSense API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router for device endpoints
from app.api.api import api_router
from app.core.config import settings
from app.db import mongodb  # Import to initialize MongoDB collections

# Add rate limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "stress_sense_db")

# MongoDB client setup
try:
    # Use the journal_collection from mongodb.py
    from app.db.mongodb import journal_collection
    logger.info("Using MongoDB journal collection")
except Exception as e:
    logger.error(f"Failed to import MongoDB collections: {e}")
    # Fallback to local setup
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    journal_collection = db["journal_entries"]
    logger.info("Connected to MongoDB successfully!")

# File paths (kept for history, but journal will use MongoDB)
# HISTORY_FILE = "stress_history.json"  # No longer needed - using database
# JOURNAL_FILE = "journal_entries.json" # No longer needed for MongoDB

# Pydantic models
class ImageData(BaseModel):
    image: str  # base64 encoded image
    timestamp: str

class JournalEntry(BaseModel):
    mood: str
    note: str
    stressLevel: str
    timestamp: str

# Removed load_history() and save_history() functions - now using database only

# MongoDB specific functions for journal entries
def load_journal_entries_from_db():
    """Load journal entries from MongoDB"""
    try:
        entries = list(journal_collection.find({}, {'_id': 0})) # Exclude _id field
        return entries
    except Exception as e:
        logger.error(f"Error loading journal entries from DB: {str(e)}")
        return []

def save_journal_entry_to_db(entry: JournalEntry):
    """Save a single journal entry to MongoDB"""
    try:
        journal_collection.insert_one(entry.dict())
    except Exception as e:
        logger.error(f"Error saving journal entry to DB: {str(e)}")

# Emotion to stress level mapping with confidence thresholds
EMOTION_STRESS_MAP = {
    "happy": {"level": "Low", "min_confidence": 25},  # Much lower threshold
    "neutral": {"level": "Low", "min_confidence": 25},
    "sad": {"level": "Medium", "min_confidence": 30},
    "angry": {"level": "Medium", "min_confidence": 30},
    "fear": {"level": "High", "min_confidence": 35},
    "disgust": {"level": "High", "min_confidence": 35},
    "surprise": {"level": "Medium", "min_confidence": 30}
}

# Suggestions based on stress levels
STRESS_SUGGESTIONS = {
    "Low": [
        "Keep up the good mood! 😊",
        "Consider sharing your positive energy with others",
        "Take a moment to appreciate your current state"
    ],
    "Medium": [
        "Try a 3-minute breathing exercise",
        "Listen to calming music",
        "Take a short walk",
        "Practice mindfulness meditation"
    ],
    "High": [
        "Stop and take deep breaths",
        "Try progressive muscle relaxation",
        "Listen to guided meditation",
        "Consider talking to someone about your feelings",
        "Take a break and do something you enjoy"
    ]
}

@app.post("/predict-stress")
async def predict_stress(data: ImageData) -> Dict:
    try:
        # Validate input
        if not data.image:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Use the updated stress analysis function
        result = analyze_image(data.image)
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Note: Not saving to history file anymore - use proper API endpoints for database storage
        logger.info(f"Successfully processed image. Stress level: {result['stress_level']}")
        return result
        
    except HTTPException as he:
        logger.warning(f"HTTPException: {he.detail}") # Log HTTP exceptions as warnings
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in predict_stress: {str(e)}", exc_info=True) # Log full traceback for unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")

@app.get("/suggestions/{level}")
async def get_suggestions(level: str) -> Dict:
    level = level.capitalize()
    if level not in STRESS_SUGGESTIONS:
        raise HTTPException(status_code=400, detail="Invalid stress level")
    
    return {
        "suggestions": STRESS_SUGGESTIONS[level]
    }

@app.get("/stress-history")
async def get_stress_history():
    """Retrieve stress prediction history from database."""
    try:
        records = get_all_stress_records(limit=100)
        # Clean MongoDB _id from results
        for record in records:
            if "_id" in record:
                record.pop("_id")
        return JSONResponse(content=records)
    except Exception as e:
        logger.error(f"Error retrieving stress history: {str(e)}")
        # Return empty list if database fails - no JSON fallback
        return JSONResponse(content=[])

@app.get("/journal-entries")
async def get_journal_entries() -> List[Dict]:
    return load_journal_entries_from_db()

@app.post("/journal-entries")
async def create_journal_entry(entry: JournalEntry) -> Dict:
    save_journal_entry_to_db(entry)
    return entry

@app.get("/")
async def root():
    return {"message": "Welcome to StressSense API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 