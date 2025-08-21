"""
Webcam capture and stress detection module for StressSense Windows Agent.
Handles capturing frames from webcam and analyzing them for stress.
"""

import cv2
import numpy as np
import base64
import logging
import time
from datetime import datetime
from deepface import DeepFace

logger = logging.getLogger(__name__)

# Emotion to stress level mapping (matches backend)
EMOTION_STRESS_MAP = {
    "happy": {"level": "Low", "min_confidence": 25},
    "neutral": {"level": "Low", "min_confidence": 25},
    "sad": {"level": "Medium", "min_confidence": 30},
    "angry": {"level": "Medium", "min_confidence": 30},
    "fear": {"level": "High", "min_confidence": 35},
    "disgust": {"level": "High", "min_confidence": 35},
    "surprise": {"level": "Medium", "min_confidence": 30}
}

class StressDetector:
    """Class for capturing webcam frames and detecting stress."""
    
    def __init__(self):
        """Initialize the stress detector."""
        self.cap = None
        self.last_frame = None
        self.warm_up_attempts = 3  # Number of frames to capture for camera warm-up
    
    def initialize_camera(self):
        """Initialize the webcam."""
        try:
            if self.cap is not None:
                self.cap.release()
            
            # List of backends to try
            backends = [
                cv2.CAP_DSHOW,      # DirectShow (Windows)
                cv2.CAP_MSMF,       # Microsoft Media Foundation (Windows)
                cv2.CAP_ANY         # Auto-detect
            ]
            
            # Try different cameras and backends
            for camera_index in range(3):  # Try cameras 0, 1, 2
                for backend in backends:
                    try:
                        logger.info(f"Trying camera {camera_index} with backend {backend}")
                        self.cap = cv2.VideoCapture(camera_index, backend)
                        
                        # Set properties for better compatibility
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                        # Check if opened successfully
                        if self.cap.isOpened():
                            # Test read a frame to confirm it works
                            ret, test_frame = self.cap.read()
                            if ret and test_frame is not None and test_frame.size > 0:
                                logger.info(f"Successfully opened camera {camera_index} with backend {backend}")
                                
                                # Warm up camera by capturing a few frames
                                for _ in range(self.warm_up_attempts):
                                    self.cap.read()  # Discard frames
                                    time.sleep(0.1)
                                
                                logger.info("Webcam initialized successfully")
                                return True
                            else:
                                logger.warning(f"Camera {camera_index} with backend {backend} opened but couldn't read frame")
                                self.cap.release()
                    except Exception as e:
                        logger.warning(f"Failed with camera {camera_index}, backend {backend}: {str(e)}")
                        if self.cap is not None:
                            self.cap.release()
                            
            logger.error("Failed to open any webcam with any backend")
            return False
        except Exception as e:
            logger.error(f"Error initializing webcam: {str(e)}")
            return False
    
    def release_camera(self):
        """Release the webcam."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("Webcam released")
    
    def capture_frame(self):
        """Capture a frame from the webcam."""
        try:
            if self.cap is None or not self.cap.isOpened():
                if not self.initialize_camera():
                    return None
            
            # Try multiple times to get a frame
            max_attempts = 3
            for attempt in range(max_attempts):
                ret, frame = self.cap.read()
                
                if ret and frame is not None and frame.size > 0:
                    self.last_frame = frame
                    logger.debug(f"Frame captured, shape: {frame.shape}")
                    return frame
                else:
                    logger.warning(f"Failed to capture frame, attempt {attempt+1}/{max_attempts}")
                    time.sleep(0.5)  # Wait before retry
                    
                    # On the second attempt, try to set properties again
                    if attempt == 1:
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                    # Try to re-initialize on the last attempt
                    if attempt == max_attempts - 1:
                        logger.info("Reinitializing camera after failed capture attempts")
                        # Full re-initialization with different backends
                        if not self.initialize_camera():
                            return None
            
            logger.error("Failed to capture frame from webcam after multiple attempts")
            return None
                
        except Exception as e:
            logger.error(f"Error capturing frame: {str(e)}")
            # If we had a previous successful frame, return it as a fallback
            if self.last_frame is not None:
                logger.info("Using last successful frame as fallback")
                return self.last_frame
            return None
    
    def detect_face(self, img):
        """Detect if a face is present in the image and return face location."""
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
    
    def check_face_quality(self, img, face_location):
        """Check if the face is well-lit and properly positioned."""
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
            
            logger.debug(f"Face quality metrics: {quality}")
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
    
    def analyze_stress(self, frame=None):
        """
        Analyze stress from a webcam frame.
        Returns:
            dict: Analysis results, or None if analysis failed
        """
        try:
            if frame is None:
                frame = self.capture_frame()
            
            if frame is None:
                logger.error("No frame to analyze")
                return None
            
            # Check if face is present
            face_detected, face_locations = self.detect_face(frame)
            if not face_detected:
                logger.warning("No face detected in the image")
                return {
                    "error": "No face detected. Please ensure your face is visible in the camera."
                }

            # Check face quality
            quality = self.check_face_quality(frame, face_locations)
            
            # Provide specific feedback based on quality issues
            if not quality["is_bright"]:
                logger.warning(f"Poor lighting detected. Brightness: {quality['brightness']}")
                return {
                    "error": "Poor lighting detected. Please ensure your face is well-lit."
                }
                
            if not quality["is_proper_size"]:
                if quality["face_ratio"] <= 0.01:
                    logger.warning(f"Face too far. Ratio: {quality['face_ratio']}")
                    return {
                        "error": "Face is too far from the camera. Please move closer."
                    }
                else:
                    logger.warning(f"Face too close. Ratio: {quality['face_ratio']}")
                    return {
                        "error": "Face is too close to the camera. Please move back."
                    }
                    
            if not quality["is_centered"]:
                logger.warning(f"Face not centered. Distance: {quality['center_distance']}")
                return {
                    "error": "Please center your face in the frame."
                }

            # Analyze emotion using DeepFace
            try:
                logger.info("Starting emotion analysis with DeepFace")
                result = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                logger.info(f"DeepFace emotion analysis successful")
            except Exception as e:
                logger.error(f"Error in DeepFace emotion analysis: {str(e)}", exc_info=True)
                return {
                    "error": "Unable to analyze emotions. Please ensure your face is clearly visible and try again."
                }
            
            # Get dominant emotion and confidence
            emotion = result[0]['dominant_emotion']
            confidence = result[0]['emotion'][emotion]
            logger.info(f"Detected emotion: {emotion} with confidence: {confidence}")
            
            # Check if confidence meets minimum threshold
            emotion_config = EMOTION_STRESS_MAP.get(emotion, {"level": "Medium", "min_confidence": 25})
            if confidence < emotion_config["min_confidence"]:
                logger.warning(f"Low confidence in emotion detection: {confidence} < {emotion_config['min_confidence']}. Emotion: {emotion}")
                return {
                    "error": "Unable to detect clear emotions. Please ensure your face is clearly visible and try again."
                }
            
            # Map emotion to stress level
            stress_level = emotion_config["level"]
            
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
                "timestamp": datetime.utcnow().isoformat() + "Z",
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
            logger.error(f"Error analyzing stress: {str(e)}", exc_info=True)
            return {
                "error": "An unexpected error occurred analyzing the image."
            }
    
    def frame_to_base64(self, frame):
        """Convert a frame to base64 encoded string."""
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting frame to base64: {str(e)}")
            return None
