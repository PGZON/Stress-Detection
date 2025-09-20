import requests
import json
import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change this to your backend URL
API_PREFIX = "/api/v1"
CONFIG_FILE = "device_config.json"

def load_config():
    """Load device configuration if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(config):
    """Save device configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def register_device(employee_id, device_name):
    """Register device with backend"""
    url = f"{BACKEND_URL}{API_PREFIX}/devices/register"

    data = {
        "employee_id": employee_id,
        "device_name": device_name,
        "device_type": "windows_agent"
    }

    logger.info(f"[DEVICE REGISTRATION] Sending registration data: {data}")
    logger.info(f"[DEVICE REGISTRATION] URL: {url}")

    try:
        response = requests.post(url, json=data)
        
        logger.info(f"[DEVICE REGISTRATION] Response status: {response.status_code}")
        logger.info(f"[DEVICE REGISTRATION] Response text: {response.text}")
        
        response.raise_for_status()

        result = response.json()
        logger.info(f"[DEVICE REGISTRATION] Registration successful: {result}")
        
        print(f"Device registered successfully!")
        print(f"Device ID: {result['device_id']}")
        print(f"API Key: {result['api_key'][:8]}...{result['api_key'][-8:]}")

        # Save configuration
        config = {
            "device_id": result['device_id'],
            "api_key": result['api_key'],
            "employee_id": employee_id,
            "registered_at": datetime.now().isoformat(),
            "backend_url": BACKEND_URL
        }
        save_config(config)

        return config

    except requests.exceptions.RequestException as e:
        logger.error(f"[DEVICE REGISTRATION] Error registering device: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"[DEVICE REGISTRATION] Response: {e.response.text}")
        print(f"Error registering device: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def main():
    print("Stress Detection Windows Agent - Device Registration")
    print("=" * 50)

    # Check if already registered
    config = load_config()
    if config:
        print("Device already registered!")
        print(f"Device ID: {config['device_id']}")
        print(f"Employee ID: {config['employee_id']}")
        print("If you want to re-register, delete device_config.json and run again.")
        return

    # Get user input
    employee_id = input("Enter your Employee ID: ").strip()
    if not employee_id:
        print("Employee ID is required!")
        return

    device_name = input("Enter device name (e.g., 'John's Laptop'): ").strip()
    if not device_name:
        device_name = f"{employee_id}'s Device"

    # Register device
    config = register_device(employee_id, device_name)
    if config:
        print("\nRegistration complete! You can now run the stress detection service.")
    else:
        print("\nRegistration failed. Please check your backend connection and try again.")

if __name__ == "__main__":
    main()