# uvicorn app:app --reload
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from deepface import DeepFace
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

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("Stress", "stress_sense_db")

# MongoDB client setup
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    journal_collection = db["journal_entries"]
    logger.info("Connected to MongoDB successfully!")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    # Exit or handle the error appropriately if MongoDB connection is critical

# File paths (kept for history, but journal will use MongoDB)
HISTORY_FILE = "stress_history.json"
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

def load_history():
    """Load stress prediction history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading history: {str(e)}")
        return []

def save_history(history):
    """Save stress prediction history to file"""
    try:
        # Convert numpy values to Python native types
        serializable_history = []
        for entry in history:
            serializable_entry = {
                "timestamp": entry["timestamp"],
                "emotion": entry["emotion"],
                "stress_level": entry["stress_level"],
                "confidence": float(entry["confidence"]),
                "face_quality": {
                    "is_bright": bool(entry["face_quality"]["is_bright"]),
                    "is_proper_size": bool(entry["face_quality"]["is_proper_size"]),
                    "is_centered": bool(entry["face_quality"]["is_centered"]),
                    "brightness": float(entry["face_quality"]["brightness"]),
                    "face_ratio": float(entry["face_quality"]["face_ratio"]),
                    "center_distance": float(entry["face_quality"]["center_distance"])
                }
            }
            serializable_history.append(serializable_entry)

        with open(HISTORY_FILE, 'w') as f:
            json.dump(serializable_history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving history: {str(e)}")

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

def detect_face(img):
    """Detect if a face is present in the image and return face location"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load the face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            logger.error("Failed to load face cascade classifier")
            return False, None

        # Very lenient face detection parameters for laptop cameras
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.02,  # More lenient scale factor
            minNeighbors=2,    # Reduced minimum neighbors
            minSize=(15, 15),  # Smaller minimum face size
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        logger.info(f"Face detection found {len(faces)} faces")
        return len(faces) > 0, faces
    except Exception as e:
        logger.error(f"Error in face detection: {str(e)}")
        return False, None

def check_face_quality(img, face_location):
    """Check if the face is well-lit and properly positioned"""
    try:
        x, y, w, h = face_location[0]
        face_roi = img[y:y+h, x:x+w]
        
        # Check brightness
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray_face)
        
        # Check face size relative to image
        img_area = img.shape[0] * img.shape[1]
        face_area = w * h
        face_ratio = face_area / img_area
        
        # Check face position (should be roughly centered)
        center_x = x + w/2
        center_y = y + h/2
        img_center_x = img.shape[1]/2
        img_center_y = img.shape[0]/2
        
        # Calculate distance from center (normalized)
        center_distance = np.sqrt(
            ((center_x - img_center_x) / img.shape[1])**2 +
            ((center_y - img_center_y) / img.shape[0])**2
        )
        
        # Very lenient quality checks for laptop cameras
        quality = {
            "is_bright": brightness > 20,  # Much lower brightness threshold
            "is_proper_size": 0.01 < face_ratio < 0.8,  # More lenient size range
            "is_centered": center_distance < 0.5,  # More lenient centering
            "brightness": float(brightness),
            "face_ratio": float(face_ratio),
            "center_distance": float(center_distance)
        }
        
        logger.info(f"Face quality metrics: {quality}")
        return quality
    except Exception as e:
        logger.error(f"Error in face quality check: {str(e)}")
        return {
            "is_bright": False,
            "is_proper_size": False,
            "is_centered": False,
            "brightness": 0,
            "face_ratio": 0,
            "center_distance": 1
        }

@app.post("/predict-stress")
async def predict_stress(data: ImageData) -> Dict:
    try:
        # Validate input
        if not data.image:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Decode base64 image
        try:
            image_data = base64.b64decode(data.image)
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            logger.info(f"Image decoded successfully. Shape: {img.shape}")
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image data format")
        
        if img is None:
            raise HTTPException(status_code=400, detail="Failed to process image data")

        # Check if face is present
        face_detected, face_locations = detect_face(img)
        if not face_detected:
            logger.warning("No face detected in the image")
            raise HTTPException(
                status_code=400,
                detail="No face detected. Please ensure your face is visible in the camera."
            )

        # Check face quality
        quality = check_face_quality(img, face_locations)
        
        # Provide specific feedback based on quality issues
        if not quality["is_bright"]:
            logger.warning(f"Poor lighting detected. Brightness: {quality['brightness']}")
            raise HTTPException(
                status_code=400,
                detail="Poor lighting detected. Please ensure your face is well-lit."
            )
        if not quality["is_proper_size"]:
            if quality["face_ratio"] <= 0.01:
                logger.warning(f"Face too far. Ratio: {quality['face_ratio']}")
                raise HTTPException(
                    status_code=400,
                    detail="Face is too far from the camera. Please move closer."
                )
            else:
                logger.warning(f"Face too close. Ratio: {quality['face_ratio']}")
                raise HTTPException(
                    status_code=400,
                    detail="Face is too close to the camera. Please move back."
                )
        if not quality["is_centered"]:
            logger.warning(f"Face not centered. Distance: {quality['center_distance']}")
            raise HTTPException(
                status_code=400,
                detail="Please center your face in the frame."
            )

        # Analyze emotion using DeepFace
        try:
            logger.info("Starting emotion analysis with DeepFace for image.")
            # Log image dimensions before analysis
            logger.info(f"Image dimensions for DeepFace: {img.shape}")
            result = DeepFace.analyze(
                img,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            logger.info(f"DeepFace emotion analysis successful. Result: {result}")
        except Exception as e:
            logger.error(f"Error in DeepFace emotion analysis: {str(e)}", exc_info=True) # Log full traceback
            raise HTTPException(
                status_code=400,
                detail="Unable to analyze emotions. Please ensure your face is clearly visible and try again."
            )
        
        # Get dominant emotion and confidence
        emotion = result[0]['dominant_emotion']
        confidence = result[0]['emotion'][emotion]
        logger.info(f"Detected emotion: {emotion} with confidence: {confidence}")
        
        # Check if confidence meets minimum threshold
        emotion_config = EMOTION_STRESS_MAP.get(emotion, {"level": "Medium", "min_confidence": 25})
        if confidence < emotion_config["min_confidence"]:
            logger.warning(f"Low confidence in emotion detection: {confidence} < {emotion_config['min_confidence']}. Emotion: {emotion}")
            raise HTTPException(
                status_code=400,
                detail="Unable to detect clear emotions. Please ensure your face is clearly visible and try again."
            )
        
        # Map emotion to stress level
        stress_level = emotion_config["level"]
        
        # Get suggestions for the stress level
        suggestions = STRESS_SUGGESTIONS.get(stress_level, [])
        
        # Create response data
        response_data = {
            "emotion": emotion,
            "stress_level": stress_level,
            "confidence": float(confidence),
            "suggestions": suggestions,
            "face_quality": {
                "is_bright": bool(quality["is_bright"]),
                "is_proper_size": bool(quality["is_proper_size"]),
                "is_centered": bool(quality["is_centered"]),
                "brightness": float(quality["brightness"]),
                "face_ratio": float(quality["face_ratio"]),
                "center_distance": float(quality["center_distance"])
            }
        }

        # Safely determine face_coords
        detected_face_coords = None
        if face_detected and isinstance(face_locations, np.ndarray) and face_locations.shape[0] > 0:
            # Ensure the first detected face has 4 coordinates (x, y, w, h)
            if len(face_locations[0]) == 4:
                detected_face_coords = face_locations[0].tolist()
        
        response_data["face_coords"] = detected_face_coords

        # Record prediction to history
        try:
            history_entry = {
                "timestamp": data.timestamp,
                "emotion": emotion,
                "stress_level": stress_level,
                "confidence": float(confidence),
                "face_quality": quality
            }
            history = load_history()
            history.append(history_entry)
            save_history(history)
        except Exception as e:
            logger.error(f"Error saving to history: {str(e)}", exc_info=True)
            # Don't fail the request if history saving fails
        
        logger.info(f"Successfully processed image. Stress level: {stress_level}")
        return response_data
        
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
    """Retrieve stress prediction history."""
    history = load_history()
    return JSONResponse(content=history)

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