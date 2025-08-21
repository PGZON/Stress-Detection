"""
Test module for StressSense Windows Agent.
Run this script to test the agent's functionality without running as a service.
"""

import os
import sys
import logging
import time
import argparse

# Add parent directory to path for direct script execution
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_config():
    """Test configuration module."""
    try:
        logger.info("Testing configuration module...")
        from windows_agent.config import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test saving and loading config
        test_config = {
            'api_url': 'http://test-api.example.com',
            'detection_interval_minutes': 15
        }
        
        config_manager.save_config(test_config)
        loaded_config = config_manager.get_config()
        
        assert loaded_config['api_url'] == test_config['api_url']
        assert loaded_config['detection_interval_minutes'] == test_config['detection_interval_minutes']
        
        # Test secure data
        test_secure_data = {
            'device_id': 'test-device-123',
            'api_key': 'test-api-key-456',
            'employee_id': 'emp-789'
        }
        
        config_manager.save_secure_data(test_secure_data)
        loaded_secure_data = config_manager.get_secure_data()
        
        assert loaded_secure_data['device_id'] == test_secure_data['device_id']
        assert loaded_secure_data['api_key'] == test_secure_data['api_key']
        assert loaded_secure_data['employee_id'] == test_secure_data['employee_id']
        
        logger.info("Configuration module tests passed")
        return True
    except Exception as e:
        logger.error(f"Configuration test failed: {str(e)}", exc_info=True)
        return False

def test_detector(capture=False):
    """
    Test stress detector module.
    
    Args:
        capture (bool): If True, capture a frame and analyze it
    """
    try:
        logger.info("Testing detector module...")
        from windows_agent.detector import StressDetector
        
        detector = StressDetector()
        
        # Test camera initialization
        success = detector.initialize_camera()
        assert success, "Camera initialization failed"
        logger.info("Camera initialized successfully")
        
        if capture:
            # Test frame capture
            frame = detector.capture_frame()
            assert frame is not None, "Frame capture failed"
            logger.info(f"Frame captured successfully, shape: {frame.shape}")
            
            # Test face detection
            face_detected, faces = detector.detect_face(frame)
            logger.info(f"Face detected: {face_detected}, found {len(faces) if faces is not None else 0} faces")
            
            if face_detected:
                # Test face quality
                quality = detector.check_face_quality(frame, faces)
                logger.info(f"Face quality: {quality}")
                
            # Test stress analysis
            result = detector.analyze_stress(frame)
            logger.info(f"Stress analysis result: {result}")
        
        # Test camera release
        detector.release_camera()
        logger.info("Camera released successfully")
        
        logger.info("Detector module tests passed")
        return True
    except Exception as e:
        logger.error(f"Detector test failed: {str(e)}", exc_info=True)
        return False

def test_api_client(test_connection=False):
    """
    Test API client module.
    
    Args:
        test_connection (bool): If True, test actual connection to API
    """
    try:
        logger.info("Testing API client module...")
        from windows_agent.api_client import APIClient
        from windows_agent.config import ConfigManager
        
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)
        
        # Check initialization
        assert api_client.api_url is not None
        logger.info(f"API client initialized with URL: {api_client.api_url}")
        
        if test_connection:
            # Test API connection
            connection_result = api_client.test_connection()
            logger.info(f"API connection test: {'Successful' if connection_result else 'Failed'}")
        
        logger.info("API client module tests passed")
        return True
    except Exception as e:
        logger.error(f"API client test failed: {str(e)}", exc_info=True)
        return False

def test_agent(run_time=10):
    """
    Test agent module by running it for a short time.
    
    Args:
        run_time (int): Number of seconds to run the agent
    """
    try:
        logger.info(f"Testing agent module for {run_time} seconds...")
        from windows_agent.agent import StressAgent
        
        agent = StressAgent()
        
        # Start the agent
        success = agent.start()
        assert success, "Agent start failed"
        logger.info("Agent started successfully")
        
        # Let it run for a few seconds
        for i in range(run_time):
            logger.info(f"Agent running... {i+1}/{run_time}")
            time.sleep(1)
        
        # Stop the agent
        success = agent.stop()
        assert success, "Agent stop failed"
        logger.info("Agent stopped successfully")
        
        logger.info("Agent module tests passed")
        return True
    except Exception as e:
        logger.error(f"Agent test failed: {str(e)}", exc_info=True)
        return False

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test StressSense Windows Agent')
    parser.add_argument('--config', action='store_true', help='Test config module')
    parser.add_argument('--detector', action='store_true', help='Test detector module')
    parser.add_argument('--capture', action='store_true', help='Test detector with frame capture')
    parser.add_argument('--api', action='store_true', help='Test API client module')
    parser.add_argument('--connect', action='store_true', help='Test API connection')
    parser.add_argument('--agent', action='store_true', help='Test agent module')
    parser.add_argument('--run-time', type=int, default=10, help='Seconds to run agent test')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.all:
        test_config()
        test_detector(args.capture)
        test_api_client(args.connect)
        test_agent(args.run_time)
    else:
        if args.config:
            test_config()
        if args.detector:
            test_detector(args.capture)
        if args.api:
            test_api_client(args.connect)
        if args.agent:
            test_agent(args.run_time)

if __name__ == "__main__":
    main()
