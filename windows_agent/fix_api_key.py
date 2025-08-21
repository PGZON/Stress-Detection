"""
API Key Fix Utility for Windows Agent
This script helps you fix API key issues by checking the current configuration
and providing options to re-register the device if needed.
"""

import os
import sys
import json
import logging
from windows_agent.config import ConfigManager
from windows_agent.api_client import APIClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_key_fix")

def check_config():
    """Check the current configuration and secure data"""
    config_manager = ConfigManager()
    
    # Check if config file exists
    config_path = config_manager.config_path
    secure_path = config_manager.secure_path
    
    print(f"\n=== Configuration Check ===")
    print(f"Config file path: {config_path}")
    print(f"Secure data path: {secure_path}")
    
    # Check config file
    if os.path.exists(config_path):
        print(f"✓ Config file exists")
        try:
            config = config_manager.get_config()
            print(f"API URL: {config.get('api_url', 'Not set')}")
        except Exception as e:
            print(f"✗ Error reading config file: {str(e)}")
    else:
        print(f"✗ Config file does not exist")
    
    # Check secure data
    if os.path.exists(secure_path):
        print(f"✓ Secure data file exists")
        try:
            secure_data = config_manager.get_secure_data()
            print(f"Device ID: {secure_data.get('device_id', 'Not set')}")
            api_key = secure_data.get('api_key', '')
            if api_key:
                # Display only first 4 and last 4 chars for security
                masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "Invalid format"
                print(f"API Key: {masked_key}")
            else:
                print(f"API Key: Not set")
            print(f"Employee ID: {secure_data.get('employee_id', 'Not set')}")
        except Exception as e:
            print(f"✗ Error reading secure data: {str(e)}")
    else:
        print(f"✗ Secure data file does not exist")
    
    # Check if the agent is configured
    is_configured = config_manager.is_configured()
    print(f"\nAgent configuration status: {'✓ Configured' if is_configured else '✗ Not fully configured'}")
    
    return is_configured, config_manager

def test_api_connection(config_manager):
    """Test the connection to the API"""
    api_client = APIClient(config_manager)
    
    print(f"\n=== API Connection Test ===")
    
    # Test basic connection
    print("Testing connection to API server...")
    connection_result = api_client.test_connection()
    if connection_result:
        print(f"✓ Connection to API server successful")
    else:
        print(f"✗ Cannot connect to API server")
        return False
    
    # If device is registered, test authentication
    secure_data = config_manager.get_secure_data()
    if secure_data.get('device_id') and secure_data.get('api_key'):
        print(f"Testing API authentication with device ID {secure_data.get('device_id')}...")
        
        # Enable more verbose debugging
        logging.getLogger("windows_agent.api_client").setLevel(logging.DEBUG)
        
        # First try with query parameter method
        print("Trying authentication with query parameter method...")
        auth_result = api_client.test_authentication()
        
        if auth_result:
            print(f"✓ Authentication successful - able to authenticate with API server")
            return True
        else:
            print(f"✗ Authentication failed with both methods")
            return False
    else:
        print("Device not registered, skipping authentication test")
        return False

def run_diagnostic_tests(config_manager):
    """Run detailed diagnostic tests for API communication"""
    api_client = APIClient(config_manager)
    secure_data = config_manager.get_secure_data()
    
    print(f"\n=== Detailed API Diagnostics ===")
    
    # Enable verbose logging for the test
    logging.getLogger("windows_agent.api_client").setLevel(logging.DEBUG)
    
    # 1. Check configuration
    print("1. Configuration check:")
    config = config_manager.get_config()
    print(f"   API URL: {config.get('api_url')}")
    print(f"   Device ID: {secure_data.get('device_id')}")
    print(f"   API Key: {secure_data.get('api_key')[:6]}..." if secure_data.get('api_key') else "   API Key: Not set")
    
    # 2. Test basic health endpoint
    print("\n2. API server health check:")
    health_result = api_client.test_connection()
    print(f"   {'✓ Passed' if health_result else '✗ Failed'} - Server health endpoint")
    
    # 3. Test authentication with query parameter
    print("\n3. Authentication test (query parameter):")
    try:
        device_id = secure_data.get('device_id')
        api_key = secure_data.get('api_key')
        
        if not device_id or not api_key:
            print("   ✗ Missing device ID or API key")
        else:
            import requests
            url = f"{config.get('api_url')}/api/v1/device/{device_id}/commands?api_key={api_key}"
            print(f"   Testing URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text[:100]}..." if len(response.text) > 100 else f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✓ Query parameter authentication successful")
            else:
                print("   ✗ Query parameter authentication failed")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # 4. Test authentication with header
    print("\n4. Authentication test (header):")
    try:
        headers = api_client._get_headers()
        print(f"   Headers: {headers}")
        
        url = f"{config.get('api_url')}/api/v1/device/{device_id}/commands"
        print(f"   Testing URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text[:100]}..." if len(response.text) > 100 else f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✓ Header authentication successful")
        else:
            print("   ✗ Header authentication failed")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # 5. Test stress submission
    print("\n5. Stress reading submission test:")
    try:
        # Create a test reading
        test_reading = {
            "stress_level": 0.2,
            "emotion": "neutral",
            "confidence": 0.95,
            "face_quality": {"quality": 0.9}
        }
        
        result = api_client.submit_stress_reading(test_reading)
        
        if result:
            print("   ✓ Stress reading submission successful")
            print(f"   Response: {result}")
        else:
            print("   ✗ Stress reading submission failed")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Reset logging level
    logging.getLogger("windows_agent.api_client").setLevel(logging.INFO)
    
    print("\nDiagnostic tests completed.")

def register_device(config_manager):
    """Register the device with the backend"""
    api_client = APIClient(config_manager)
    
    print(f"\n=== Device Registration ===")
    
    # Ask for employee ID
    employee_id = input("Enter employee ID: ").strip()
    if not employee_id:
        print("Employee ID is required")
        return False
    
    # Ask for device name
    device_name = input("Enter device name (or press Enter for default): ").strip()
    if not device_name:
        import socket
        device_name = socket.gethostname()
        print(f"Using hostname as device name: {device_name}")
    
    # Confirm registration
    print(f"\nRegistering device with:")
    print(f"Employee ID: {employee_id}")
    print(f"Device Name: {device_name}")
    confirm = input("\nProceed with registration? (y/n): ").lower()
    
    if confirm != 'y':
        print("Registration cancelled")
        return False
    
    # Register the device
    print("\nRegistering device...")
    result = api_client.register_device(employee_id, device_name)
    
    if result:
        print(f"✓ Device registered successfully")
        print(f"Device ID: {result.get('device_id')}")
        # Display only first 4 and last 4 chars of API key for security
        api_key = result.get('api_key', '')
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "Invalid format"
        print(f"API Key: {masked_key}")
        
        # Test the new registration
        print("\nTesting new registration...")
        if test_api_connection(config_manager):
            print("✓ New registration is working correctly")
            return True
        else:
            print("✗ New registration test failed")
            return False
    else:
        print("✗ Registration failed")
        return False

def fix_api_key():
    """Main function to fix API key issues"""
    print("\n======================================")
    print("  Windows Agent API Key Fix Utility")
    print("======================================\n")
    
    # Check current configuration
    is_configured, config_manager = check_config()
    
    # If configured, test the connection
    if is_configured:
        connection_works = test_api_connection(config_manager)
        
        if connection_works:
            print("\n✓ Your API key is working correctly!")
            print("No fixes needed.")
            
            # Ask if user wants to run diagnostics anyway
            action = input("\nWould you like to run advanced diagnostics? (y/n): ").lower()
            if action == 'y':
                run_diagnostic_tests(config_manager)
            
            return True
        else:
            print("\n✗ Your API key is not working correctly.")
            
            # Run diagnostics automatically in case of failure
            print("\nRunning advanced diagnostics to identify the issue...")
            run_diagnostic_tests(config_manager)
            
            # Ask if user wants to register again
            action = input("\nWould you like to re-register the device? (y/n): ").lower()
            if action == 'y':
                return register_device(config_manager)
            else:
                print("\nNo changes made. Please contact your administrator for assistance.")
                return False
    else:
        print("\nYour device is not fully configured.")
        
        # Ask if user wants to register
        action = input("\nWould you like to register the device now? (y/n): ").lower()
        if action == 'y':
            return register_device(config_manager)
        else:
            print("\nNo changes made. Please contact your administrator for assistance.")
            return False

if __name__ == "__main__":
    success = fix_api_key()
    if success:
        print("\n✓ API key issues have been resolved!")
    else:
        print("\n✗ API key issues could not be resolved. Please contact your administrator.")
    
    input("\nPress Enter to exit...")
