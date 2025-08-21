"""
API client module for StressSense Windows Agent.
Handles communication with the backend API.
"""

import requests
import json
import logging
import time
from datetime import datetime, timedelta  # Add timedelta import

from windows_agent.config import ConfigManager

logger = logging.getLogger(__name__)

class APIClient:
    """Client for interacting with the backend API."""
    
    def __init__(self, config_manager=None):
        """
        Initialize the API client.
        
        Args:
            config_manager: ConfigManager instance for accessing configuration
        """
        self.config_manager = config_manager or ConfigManager()
        self.api_url = self.config_manager.get_config().get('api_url', 'http://localhost:8000')
        
        # Load secure data - ensure we're getting fresh data
        secure_data = self.config_manager.get_secure_data()
        self.api_key = secure_data.get('api_key')
        self.device_id = secure_data.get('device_id')
        self.employee_id = secure_data.get('employee_id')
        
        logger.debug(f"Initialized API client with device_id: {self.device_id} and API key exists: {bool(self.api_key)}")
        self.session = requests.Session()
    
    def _get_headers(self):
        """Get headers for API requests."""
        if not self.api_key:
            # Reload secure data in case it was updated elsewhere
            secure_data = self.config_manager.get_secure_data()
            self.api_key = secure_data.get('api_key')
            
        headers = {
            'X-Device-Key': self.api_key if self.api_key else '',  # Primary header method
            'Content-Type': 'application/json'
        }
        logger.debug(f"Generated headers with API key: {self.api_key[:4] if self.api_key else None}...{self.api_key[-4:] if self.api_key else None}")
        return headers
    
    def test_connection(self):
        """
        Test the connection to the API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Fix: Correct health endpoint URL
            url = f"{self.api_url}/api/v1/utils/health"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("API connection test successful")
                return True
            else:
                logger.error(f"API connection test failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error testing API connection: {str(e)}")
            return False
        
    def test_authentication(self):
        """
        Test if the API key is valid.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Reload secure data to get the latest API key and device ID
            secure_data = self.config_manager.get_secure_data()
            self.api_key = secure_data.get('api_key')
            self.device_id = secure_data.get('device_id')
            
            if not self.device_id or not self.api_key:
                logger.error("Device not registered. Cannot test authentication.")
                return False
            
            logger.debug(f"Testing authentication with device_id: {self.device_id} and API key: {self.api_key[:4]}...{self.api_key[-4:]}")
                
            # First try using URL query parameter for API key
            url = f"{self.api_url}/api/v1/device/{self.device_id}/commands?api_key={self.api_key}"
            
            # Debug the request
            logger.debug(f"Authentication request (query param): URL={url}")
            
            response = self.session.get(
                url,
                timeout=10
            )
            
            # Debug the response
            logger.debug(f"Authentication response (query param): Status={response.status_code}, Body={response.text}")
            
            # If query parameter method fails, try header method
            if response.status_code != 200:
                logger.debug("Query parameter authentication failed, trying header method")
                url = f"{self.api_url}/api/v1/device/{self.device_id}/commands"
                headers = self._get_headers()
                
                # Debug the headers to ensure they're correct
                logger.debug(f"Authentication request (header): URL={url}, Headers={headers}")
                
                response = self.session.get(
                    url, 
                    headers=headers,
                    timeout=10
                )
                
                # Debug the response
                logger.debug(f"Authentication response (header): Status={response.status_code}, Body={response.text}")
            
            if response.status_code == 200:
                logger.info("API authentication test successful")
                return True
            elif response.status_code == 401:
                logger.error(f"API authentication test failed: Invalid API key")
                # Log the response to debug
                logger.debug(f"Authentication response: {response.status_code} {response.text}")
                return False
            else:
                logger.error(f"API authentication test failed: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error testing API authentication: {str(e)}")
            return False
    
    def register_device(self, employee_id=None, device_name=None):
        """
        Register this device with the API and obtain device_id and API key.
        
        Args:
            employee_id: Employee ID to register with
            device_name: Name for this device
            
        Returns:
            dict: Registration response or None if failed
        """
        try:
            employee_id = employee_id or self.employee_id
            
            if not employee_id:
                logger.error("No employee_id provided for device registration")
                return None
            
            import platform
            import socket
            
            # Get system information if device name not provided
            if not device_name:
                hostname = socket.gethostname()
                system = platform.system()
                release = platform.release()
                device_name = f"{hostname} ({system} {release})"
                
            url = f"{self.api_url}/api/v1/device/register"
            
            data = {
                "employee_id": employee_id,
                "device_name": device_name,
                "device_type": "windows_agent",
                "registration_date": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.debug(f"Registering device with data: {data}")
            response = self.session.post(url, json=data, timeout=15)
            
            if response.status_code == 201:
                result = response.json()
                self.device_id = result.get('device_id')
                self.api_key = result.get('api_key')
                self.employee_id = employee_id
                
                # Save the registration data
                secure_data = {
                    'device_id': self.device_id,
                    'api_key': self.api_key,
                    'employee_id': self.employee_id
                }
                self.config_manager.save_secure_data(secure_data)
                
                logger.info(f"Device registered successfully: {self.device_id}")
                logger.debug(f"API key received: {self.api_key[:4]}...{self.api_key[-4:]}")
                return result
            else:
                logger.error(f"Device registration failed: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error registering device: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error registering device: {str(e)}")
            return None
    
    def submit_stress_reading(self, reading_data):
        """
        Submit a stress reading to the API.
        
        Args:
            reading_data (dict): Stress reading data
            
        Returns:
            dict: Response data or None if failed
        """
        try:
            if not self.device_id or not self.api_key:
                logger.error("Device not registered. Cannot submit stress reading.")
                return None
                
            # Use the correct endpoint path
            url = f"{self.api_url}/api/v1/stress/record"
            
            # Convert numerical stress level to string enum value
            stress_level = reading_data.get("stress_level")
            if isinstance(stress_level, (int, float)):
                if stress_level <= 0.33:
                    stress_level = "Low"
                elif stress_level <= 0.66:
                    stress_level = "Medium"
                else:
                    stress_level = "High"
            
            # Map emotions to allowed values
            emotion = reading_data.get("emotion", "neutral")
            allowed_emotions = ["happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"]
            emotion_map = {
                "stressed": "angry",
                "calm": "neutral",
                "relaxed": "happy",
                "worried": "fear",
                "anxious": "fear"
            }
            
            if emotion not in allowed_emotions and emotion in emotion_map:
                emotion = emotion_map[emotion]
            elif emotion not in allowed_emotions:
                emotion = "neutral"  # Default to neutral if unknown
            
            # Ensure required fields are present
            data = {
                "device_id": self.device_id,
                "employee_id": self.employee_id,
                "stress_level": stress_level,
                "emotion": emotion,
                "confidence": reading_data.get("confidence"),
                "timestamp": reading_data.get("timestamp") or datetime.utcnow().isoformat() + "Z",
                "metadata": {
                    "face_quality": reading_data.get("face_quality", {}),
                    "face_coords": reading_data.get("face_coords")
                }
            }
            
            logger.debug(f"Prepared stress reading data: {data}")
            
            # Try first with query parameter method
            query_url = f"{url}?api_key={self.api_key}"
            logger.debug(f"Submitting stress reading to {query_url}")
            
            response = self.session.post(
                query_url, 
                json=data,
                timeout=15
            )
            
            # If query parameter method fails, try with header method
            if response.status_code in (401, 403):
                logger.debug("Query parameter submission failed, trying header method")
                response = self.session.post(
                    url, 
                    json=data,
                    headers=self._get_headers(),
                    timeout=15
                )
            
            if response.status_code in (200, 201):
                logger.info("Stress reading submitted successfully")
                return response.json()
            elif response.status_code == 401:
                error_msg = f"Failed to submit stress reading: 401 {response.text} - API key may be invalid"
                logger.error(error_msg)
                logger.info("Run 'fix_api_key.bat' to troubleshoot API key issues")
                return None
            else:
                logger.error(f"Failed to submit stress reading: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error submitting stress reading: {str(e)}")
            return None
    
    def get_device_commands(self):
        """
        Fetch pending commands for this device.
        
        Returns:
            list: List of command objects or empty list if none/error
        """
        try:
            if not self.device_id or not self.api_key:
                logger.error("Device not registered. Cannot fetch commands.")
                return []
                
            # Add API key as a query parameter for additional compatibility
            url = f"{self.api_url}/api/v1/device/{self.device_id}/commands?api_key={self.api_key}"
            
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                commands = response.json()
                logger.info(f"Fetched {len(commands)} device commands")
                return commands
            else:
                logger.error(f"Failed to fetch device commands: {response.status_code} {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching device commands: {str(e)}")
            return []
    
    def acknowledge_command(self, command_id, status="completed", response=None):
        """
        Acknowledge a command as processed.
        
        Args:
            command_id (str): ID of the command to acknowledge
            status (str): Status of command execution (completed, failed)
            response (dict): Optional response data
            
        Returns:
            bool: True if acknowledged successfully, False otherwise
        """
        try:
            if not self.device_id or not self.api_key:
                logger.error("Device not registered. Cannot acknowledge command.")
                return False
                
            # Fix: Correct endpoint path
            url = f"{self.api_url}/api/v1/device/commands/ack/{command_id}"
            
            data = {
                "status": status,
                "processed_at": datetime.utcnow().isoformat() + "Z",
                "response": response or {}
            }
            
            response = self.session.post(
                url,
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Command {command_id} acknowledged with status: {status}")
                return True
            else:
                logger.error(f"Failed to acknowledge command: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error acknowledging command: {str(e)}")
            return False
    
    def get_employee_stress_history(self, days=7):
        """
        Get stress history for the current employee.
        
        Args:
            days (int): Number of days to retrieve
            
        Returns:
            dict: Response with stress history data
        """
        try:
            # Check if device is registered
            if not self.device_id or not self.api_key or not self.employee_id:
                logger.warning("Device not registered, cannot get stress history")
                return {'success': False, 'message': 'Device not registered'}
                
            url = f"{self.api_url}/api/v1/employee/stress/history/{self.employee_id}"
            params = {'days': days}
            
            response = self.session.get(
                url, 
                params=params,
                headers=self._get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Failed to get stress history: {response.status_code} {response.text}")
                return {'success': False, 'message': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error getting stress history: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def trigger_analyze_now(self):
        """
        Trigger an immediate stress analysis.
        
        Returns:
            dict: Response indicating success or failure
        """
        try:
            # Check if device is registered
            if not self.device_id or not self.api_key:
                logger.warning("Device not registered, cannot trigger analysis")
                return {'success': False, 'message': 'Device not registered'}
                
            # Fix: Correct endpoint path
            url = f"{self.api_url}/api/v1/device/{self.device_id}/commands"
            
            data = {
                "command_type": "analyze_now",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
            }
            
            response = self.session.post(
                url, 
                json=data,
                headers=self._get_headers(),
                timeout=15
            )
            
            if response.status_code in (200, 201):
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Failed to trigger analysis: {response.status_code} {response.text}")
                return {'success': False, 'message': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error triggering analysis: {str(e)}")
            return {'success': False, 'message': str(e)}
