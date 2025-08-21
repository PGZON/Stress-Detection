import cv2
import numpy as np
from deepface import DeepFace
import logging
from app.core.config import settings
import base64
from typing import Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)

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

def analyze_image(image_data: str) -> Dict[str, Any]:
    """
    Analyze an image for emotion detection and stress analysis
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        logger.info(f"Image decoded successfully. Shape: {img.shape}")
        
        if img is None:
            return {"error": "Failed to process image data"}

        # Check if face is present
        face_detected, face_locations = detect_face(img)
        if not face_detected:
            logger.warning("No face detected in the image")
            return {"error": "No face detected. Please ensure your face is visible in the camera."}

        # Check face quality
        quality = check_face_quality(img, face_locations)
        
        # Provide specific feedback based on quality issues
        if not quality["is_bright"]:
            logger.warning(f"Poor lighting detected. Brightness: {quality['brightness']}")
            return {"error": "Poor lighting detected. Please ensure your face is well-lit."}
            
        if not quality["is_proper_size"]:
            if quality["face_ratio"] <= 0.01:
                logger.warning(f"Face too far. Ratio: {quality['face_ratio']}")
                return {"error": "Face is too far from the camera. Please move closer."}
            else:
                logger.warning(f"Face too close. Ratio: {quality['face_ratio']}")
                return {"error": "Face is too close to the camera. Please move back."}
                
        if not quality["is_centered"]:
            logger.warning(f"Face not centered. Distance: {quality['center_distance']}")
            return {"error": "Please center your face in the frame."}

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
            logger.error(f"Error in DeepFace emotion analysis: {str(e)}", exc_info=True)
            return {"error": "Unable to analyze emotions. Please ensure your face is clearly visible and try again."}
        
        # Get dominant emotion and confidence
        emotion = result[0]['dominant_emotion']
        confidence = result[0]['emotion'][emotion]
        logger.info(f"Detected emotion: {emotion} with confidence: {confidence}")
        
        # Check if confidence meets minimum threshold
        emotion_config = settings.EMOTION_STRESS_MAP.get(emotion, {"level": "Medium", "min_confidence": 25})
        if confidence < emotion_config["min_confidence"]:
            logger.warning(f"Low confidence in emotion detection: {confidence} < {emotion_config['min_confidence']}. Emotion: {emotion}")
            return {"error": "Unable to detect clear emotions. Please ensure your face is clearly visible and try again."}
        
        # Map emotion to stress level
        stress_level = emotion_config["level"]
        
        # Get suggestions for the stress level
        suggestions = settings.STRESS_SUGGESTIONS.get(stress_level, [])
        
        # Safely determine face_coords
        detected_face_coords = None
        if face_detected and isinstance(face_locations, np.ndarray) and face_locations.shape[0] > 0:
            # Ensure the first detected face has 4 coordinates (x, y, w, h)
            if len(face_locations[0]) == 4:
                detected_face_coords = face_locations[0].tolist()
        
        # Create result
        result = {
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
            },
            "face_coords": detected_face_coords
        }
        
        logger.info(f"Successfully processed image. Stress level: {stress_level}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred analyzing the image."}
