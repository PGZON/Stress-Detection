"""
Main entry point for StressSense Windows Agent.
"""

import os
import sys
import logging
import argparse
import threading
from windows_agent.agent import StressAgent
from windows_agent.config import ConfigManager
from windows_agent.api_client import APIClient
from windows_agent.wellness_assistant import run as run_wellness_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/StressSense/agent.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def register_device(employee_id, device_name=None):
    """
    Register a device with the backend.
    
    Args:
        employee_id (str): Employee ID to register with
        device_name (str, optional): Name for this device
    
    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)
        
        result = api_client.register_device(employee_id, device_name)
        
        if result:
            print(f"Device registered successfully!")
            print(f"Device ID: {result.get('device_id')}")
            return True
        else:
            print("Device registration failed.")
            return False
    except Exception as e:
        print(f"Error during device registration: {str(e)}")
        return False

def run_agent(with_wellness_assistant=True):
    """Run the stress detection agent."""
    try:
        config_manager = ConfigManager()
        
        # Check if device is registered
        secure_data = config_manager.get_secure_data()
        if not secure_data.get('device_id') or not secure_data.get('api_key'):
            logger.error("Device not registered. Please register the device first.")
            print("Device not registered. Use --register to register this device.")
            sys.exit(1)
            
        # Check API key validity
        api_client = APIClient(config_manager)
        if not api_client.test_authentication():
            logger.error("API key authentication failed. You may need to re-register this device.")
            print("\nAPI key authentication failed. You may need to re-register this device.")
            print("Run 'fix_api_key.bat' to troubleshoot API key issues.")
            sys.exit(1)
            
        # Start the agent
        agent = StressAgent()
        
        if agent.start():
            # Start wellness assistant if requested
            if with_wellness_assistant:
                logger.info("Starting wellness assistant...")
                wellness_thread = threading.Thread(
                    target=run_wellness_assistant,
                    name="WellnessAssistantThread",
                    daemon=True
                )
                wellness_thread.start()
            
            # Keep main thread alive
            try:
                while True:
                    import time
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                agent.stop()
        else:
            logger.error("Failed to start agent")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}", exc_info=True)
        sys.exit(1)

def configure(api_url=None):
    """
    Configure the agent.
    
    Args:
        api_url (str, optional): API URL to configure
    
    Returns:
        bool: True if configuration successful, False otherwise
    """
    try:
        config_manager = ConfigManager()
        current_config = config_manager.get_config()
        
        if api_url:
            current_config['api_url'] = api_url
            
        # Allow interactive configuration
        print("StressSense Agent Configuration")
        print("-" * 30)
        
        if 'api_url' not in current_config:
            current_config['api_url'] = input("Backend API URL [http://localhost:8000]: ").strip() or "http://localhost:8000"
        
        detection_interval = input(f"Detection interval (minutes) [{current_config.get('detection_interval_minutes', 30)}]: ").strip()
        if detection_interval and detection_interval.isdigit():
            current_config['detection_interval_minutes'] = int(detection_interval)
        elif 'detection_interval_minutes' not in current_config:
            current_config['detection_interval_minutes'] = 30
        
        # Save configuration
        config_manager.save_config(current_config)
        print("Configuration saved successfully.")
        return True
    except Exception as e:
        print(f"Error during configuration: {str(e)}")
        return False

def test_connection():
    """Test the connection to the backend API."""
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)
        
        print(f"Testing connection to {api_client.api_url}...")
        if api_client.test_connection():
            print("Connection successful!")
            return True
        else:
            print("Connection failed.")
            return False
    except Exception as e:
        print(f"Error testing connection: {str(e)}")
        return False

def show_status():
    """Show the status of the agent."""
    try:
        config_manager = ConfigManager()
        secure_data = config_manager.get_secure_data()
        config = config_manager.get_config()
        
        print("StressSense Agent Status")
        print("-" * 30)
        
        if secure_data.get('device_id'):
            print(f"Device ID: {secure_data.get('device_id')}")
            print(f"Employee ID: {secure_data.get('employee_id')}")
            print(f"API Key: {'*' * 8}{secure_data.get('api_key')[-4:] if secure_data.get('api_key') else 'Not set'}")
        else:
            print("Device not registered. Use --register to register this device.")
            
        print(f"API URL: {config.get('api_url', 'Not configured')}")
        print(f"Detection Interval: {config.get('detection_interval_minutes', 30)} minutes")
        
        # Test connection
        api_client = APIClient(config_manager)
        connection_status = "OK" if api_client.test_connection() else "Failed"
        print(f"API Connection: {connection_status}")
        
        # Test authentication if device is registered
        if secure_data.get('device_id') and secure_data.get('api_key'):
            auth_status = "OK" if api_client.test_authentication() else "Failed"
            print(f"API Authentication: {auth_status}")
            
            if auth_status == "Failed":
                print("\nAPI key authentication failed. You may need to re-register this device.")
                print("Run 'fix_api_key.bat' to troubleshoot API key issues.")
        
        return True
    except Exception as e:
        print(f"Error showing status: {str(e)}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='StressSense Windows Agent')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--run', action='store_true', help='Run the agent')
    group.add_argument('--register', metavar='EMPLOYEE_ID', help='Register this device')
    group.add_argument('--device-name', metavar='NAME', help='Specify device name for registration')
    group.add_argument('--configure', action='store_true', help='Configure the agent')
    group.add_argument('--api-url', metavar='URL', help='Set API URL')
    group.add_argument('--test-connection', action='store_true', help='Test connection to API')
    group.add_argument('--wellness', action='store_true', help='Run only the wellness assistant')
    group.add_argument('--status', action='store_true', help='Show agent status')
    
    args = parser.parse_args()
    
    if args.register:
        register_device(args.register, args.device_name)
    elif args.configure:
        configure(args.api_url)
    elif args.api_url:
        configure(args.api_url)
    elif args.test_connection:
        test_connection()
    elif args.status:
        show_status()
    elif args.wellness:
        # Run only the wellness assistant (without background agent)
        run_wellness_assistant()
    else:
        # Default to running the agent with wellness assistant
        run_agent(with_wellness_assistant=True)

if __name__ == "__main__":
    main()