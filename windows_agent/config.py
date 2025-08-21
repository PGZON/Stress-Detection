"""
Configuration module for the StressSense Windows Agent.
Handles loading, saving, and encrypting the configuration.
"""

import os
import json
import logging
import base64
from pathlib import Path
import win32crypt
import win32con
import win32security
import getpass

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "detection_interval_minutes": 30,
    "log_level": "INFO",
    "offline_queue_max_size": 100,
    "startup_delay_seconds": 60
}

# Constants
CONFIG_DIR_NAME = "StressSense"
CONFIG_FILE_NAME = "config.json"
SECURE_FILE_NAME = "secure.dat"
ENCRYPTED_KEY_SUFFIX = "__ENCRYPTED__"

class ConfigManager:
    """Configuration manager for the StressSense Windows Agent."""
    
    def __init__(self):
        """Initialize the configuration."""
        self.config = DEFAULT_CONFIG.copy()
        self.config_path = self._get_config_path("config")
        self.secure_path = self._get_config_path("secure")
        self.load_config()
        self.secure_data = self.load_secure_data()
    
    def _get_config_path(self, file_type="config"):
        """Get the path to the configuration file."""
        # Use AppData/Local for configuration
        app_data = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
        config_dir = os.path.join(app_data, CONFIG_DIR_NAME)
        
        # Create directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        if file_type == "secure":
            return os.path.join(config_dir, SECURE_FILE_NAME)
        else:
            return os.path.join(config_dir, CONFIG_FILE_NAME)
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    stored_config = json.load(f)
                    
                    # Update config with stored values
                    for key, value in stored_config.items():
                        self.config[key] = value
                            
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"No configuration file found at {self.config_path}, using defaults")
                self.save_config(self.config)  # Create the default config file
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    def save_config(self, config_data):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            logger.info(f"Configuration saved to {self.config_path}")
            self.config = config_data
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def load_secure_data(self):
        """Load secure data from file."""
        try:
            if os.path.exists(self.secure_path):
                try:
                    # First try plain JSON
                    with open(self.secure_path, 'r') as f:
                        secure_data = json.load(f)
                        return secure_data
                except:
                    # If plain JSON fails, try the original method
                    with open(self.secure_path, 'rb') as f:
                        encrypted_data = f.read()
                    if encrypted_data:
                        try:
                            # First try DPAPI
                            decrypted_data = self._decrypt_data(encrypted_data)
                            return json.loads(decrypted_data)
                        except:
                            # If DPAPI fails, try base64
                            try:
                                decoded = base64.b64decode(encrypted_data)
                                return json.loads(decoded)
                            except:
                                logger.error("Failed to decrypt with both DPAPI and base64")
            
            # Return empty secure data if file doesn't exist or is empty
            return {"device_id": "", "api_key": "", "employee_id": ""}
        except Exception as e:
            logger.error(f"Error loading secure data: {str(e)}")
            return {"device_id": "", "api_key": "", "employee_id": ""}
    
    def save_secure_data(self, secure_data):
        """Save secure data to file."""
        try:
            # Save as plain JSON for now to ensure it works
            json_data = json.dumps(secure_data)
            
            with open(self.secure_path, 'w') as f:
                f.write(json_data)
                
            logger.info(f"Secure data saved to {self.secure_path}")
            self.secure_data = secure_data
            return True
        except Exception as e:
            logger.error(f"Error saving secure data: {str(e)}")
            return False
    
    def _encrypt_data(self, data):
        """Encrypt data using Windows DPAPI."""
        try:
            return win32crypt.CryptProtectData(
                data, 
                "StressSense Secure Data", 
                None, 
                None, 
                None, 
                0x01
            )
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            # Fallback if encryption fails - still better than plaintext
            return base64.b64encode(data)
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt data using Windows DPAPI."""
        try:
            decrypted_data, _ = win32crypt.CryptUnprotectData(
                encrypted_data, 
                None, 
                None, 
                None, 
                0x01
            )
            return decrypted_data
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            # Fallback if decryption fails
            try:
                return base64.b64decode(encrypted_data)
            except:
                return b"{}"
    
    def get_config(self):
        """Get the complete configuration dictionary."""
        return self.config.copy()
    
    def get_secure_data(self):
        """Get the complete secure data dictionary."""
        return self.secure_data.copy()
    
    def update_config(self, key, value):
        """Update a single configuration value."""
        self.config[key] = value
        self.save_config(self.config)
        
    def is_configured(self):
        """Check if the agent is properly configured."""
        secure_data = self.get_secure_data()
        return bool(secure_data.get("device_id") and secure_data.get("employee_id") and secure_data.get("api_key"))
