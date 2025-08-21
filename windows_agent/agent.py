"""
Main agent module for StressSense Windows Agent.
Handles background operation, scheduling of stress detection, 
and command processing.
"""

import os
import time
import logging
import threading
import signal
import sys
import json
import queue
import random
from datetime import datetime, timedelta

# Import other modules
from windows_agent.detector import StressDetector
from windows_agent.api_client import APIClient
from windows_agent.config import ConfigManager


# Ensure log directory exists
log_dir = os.path.expanduser('~/StressSense')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'agent.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StressAgent:
    """Main stress detection agent class."""
    
    def __init__(self):
        """Initialize the stress agent."""
        self.config_manager = ConfigManager()
        self.detector = StressDetector()
        self.api_client = APIClient(self.config_manager)
        self.running = False
        self.command_queue = queue.Queue()
        self.last_detection_time = None
        self.detection_thread = None
        self.command_thread = None
        self.config = self.config_manager.get_config()
        self.random_offset = 0  # For randomized interval
    
    def start(self):
        """Start the stress agent."""
        try:
            logger.info("Starting StressSense Agent")
            
            # Create necessary directories
            log_dir = os.path.expanduser('~/StressSense')
            os.makedirs(log_dir, exist_ok=True)
            
            # Set running flag
            self.running = True
            
            # Check if device is registered
            secure_data = self.config_manager.get_secure_data()
            if not secure_data.get('device_id') or not secure_data.get('api_key'):
                logger.warning("Device not registered. Please register the device first.")
            else:
                logger.info(f"Device ID: {secure_data.get('device_id')}")
            
            # Initialize camera
            if not self.detector.initialize_camera():
                logger.error("Failed to initialize camera")
                
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start threads
            self._start_detection_thread()
            self._start_command_thread()
            
            logger.info("StressSense Agent started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting agent: {str(e)}", exc_info=True)
            return False
    
    def stop(self):
        """Stop the stress agent."""
        try:
            logger.info("Stopping StressSense Agent")
            self.running = False
            
            # Wait for threads to exit
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=5.0)
            
            if self.command_thread and self.command_thread.is_alive():
                self.command_thread.join(timeout=5.0)
            
            # Release camera
            self.detector.release_camera()
            
            logger.info("StressSense Agent stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping agent: {str(e)}", exc_info=True)
            return False
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {sig}")
        self.stop()
        sys.exit(0)
    
    def _start_detection_thread(self):
        """Start the stress detection thread."""
        self.detection_thread = threading.Thread(
            target=self._detection_loop,
            name="StressDetectionThread",
            daemon=True
        )
        self.detection_thread.start()
    
    def _start_command_thread(self):
        """Start the command processing thread."""
        self.command_thread = threading.Thread(
            target=self._command_loop,
            name="CommandProcessingThread",
            daemon=True
        )
        self.command_thread.start()
    
    def _detection_loop(self):
        """Main loop for scheduled stress detection."""
        while self.running:
            try:
                # Get updated config
                self.config = self.config_manager.get_config()
                interval_minutes = self.config.get('detection_interval_minutes', 30)
                
                # Should we detect stress now?
                should_detect = False
                
                # Check if it's time for scheduled detection
                if (self.last_detection_time is None or
                    (datetime.now() - self.last_detection_time).total_seconds() >= 
                    (interval_minutes * 60) + self.random_offset):
                    should_detect = True
                    # Set new random offset between -5 and +5 minutes
                    self.random_offset = random.randint(-300, 300)
                
                # Check for manual detection command
                try:
                    # Non-blocking queue check
                    command = self.command_queue.get_nowait()
                    if command.get('type') == 'analyze_now':
                        should_detect = True
                        logger.info("Processing manual detection command")
                        command_id = command.get('command_id')
                    self.command_queue.task_done()
                except queue.Empty:
                    command_id = None
                
                # Perform detection if needed
                if should_detect and self.running:
                    self._perform_stress_detection(command_id)
                    self.last_detection_time = datetime.now()
                
                # Sleep for a short time before checking again
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {str(e)}", exc_info=True)
                time.sleep(30)  # Sleep longer after an error
    
    def _command_loop(self):
        """Loop for checking and processing commands from the API."""
        while self.running:
            try:
                # Check for commands every 2 minutes
                commands = self.api_client.get_device_commands()
                
                for command in commands:
                    command_type = command.get('command_type')
                    command_id = command.get('command_id')
                    
                    if command_type == 'analyze_now':
                        # Queue for immediate stress detection
                        self.command_queue.put({
                            'type': 'analyze_now',
                            'command_id': command_id
                        })
                        logger.info(f"Queued analyze_now command {command_id}")
                    
                    elif command_type == 'update_config':
                        # Update configuration
                        try:
                            new_config = json.loads(command.get('payload', '{}'))
                            if new_config:
                                current_config = self.config_manager.get_config()
                                current_config.update(new_config)
                                self.config_manager.save_config(current_config)
                                self.config = current_config
                                logger.info(f"Updated configuration from command {command_id}")
                                
                                # Acknowledge command
                                self.api_client.acknowledge_command(
                                    command_id, 
                                    "completed",
                                    {"message": "Configuration updated successfully"}
                                )
                            else:
                                # Acknowledge command with failure
                                self.api_client.acknowledge_command(
                                    command_id, 
                                    "failed",
                                    {"error": "Invalid configuration payload"}
                                )
                        except Exception as e:
                            logger.error(f"Error processing update_config command: {str(e)}")
                            # Acknowledge command with failure
                            self.api_client.acknowledge_command(
                                command_id, 
                                "failed",
                                {"error": f"Error updating configuration: {str(e)}"}
                            )
                    
                    elif command_type == 'restart_agent':
                        # Acknowledge and schedule restart
                        logger.info(f"Received restart command {command_id}")
                        self.api_client.acknowledge_command(
                            command_id, 
                            "completed",
                            {"message": "Agent restart initiated"}
                        )
                        
                        # Schedule a restart
                        threading.Timer(3.0, self._restart_agent).start()
                    
                    else:
                        # Unknown command type
                        logger.warning(f"Unknown command type: {command_type}")
                        self.api_client.acknowledge_command(
                            command_id, 
                            "failed",
                            {"error": f"Unknown command type: {command_type}"}
                        )
                
                # Sleep between command checks
                time.sleep(120)  # 2 minutes
                
            except Exception as e:
                logger.error(f"Error in command loop: {str(e)}", exc_info=True)
                time.sleep(60)  # Sleep 1 minute after an error
    
    def _perform_stress_detection(self, command_id=None):
        """
        Perform stress detection and submit results.
        
        Args:
            command_id (str, optional): Command ID if triggered manually
        """
        try:
            logger.info("Performing stress detection")
            
            # Analyze stress from webcam
            result = self.detector.analyze_stress()
            
            if not result:
                logger.error("Stress detection failed - no result")
                if command_id:
                    self.api_client.acknowledge_command(
                        command_id, 
                        "failed",
                        {"error": "Stress detection failed to produce a result"}
                    )
                return
            
            # Check for error in result
            if result.get('error'):
                logger.warning(f"Stress detection issue: {result['error']}")
                if command_id:
                    self.api_client.acknowledge_command(
                        command_id, 
                        "failed",
                        {"error": result['error']}
                    )
                return
            
            # Submit to API
            api_result = self.api_client.submit_stress_reading(result)
            
            # If this was triggered by a command, acknowledge it
            if command_id:
                status = "completed" if api_result else "failed"
                response = {
                    "stress_level": result.get('stress_level'),
                    "emotion": result.get('emotion'),
                    "confidence": result.get('confidence'),
                    "api_submission": "successful" if api_result else "failed"
                }
                self.api_client.acknowledge_command(command_id, status, response)
            
        except Exception as e:
            logger.error(f"Error in stress detection: {str(e)}", exc_info=True)
            if command_id:
                self.api_client.acknowledge_command(
                    command_id, 
                    "failed",
                    {"error": f"Exception during stress detection: {str(e)}"}
                )
    
    def _restart_agent(self):
        """Restart the agent."""
        try:
            logger.info("Restarting agent...")
            self.stop()
            time.sleep(1)
            self.start()
        except Exception as e:
            logger.error(f"Error restarting agent: {str(e)}", exc_info=True)


def run():
    """Run the stress agent as a standalone process."""
    agent = StressAgent()
    
    if agent.start():
        # Keep main thread alive
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            agent.stop()
    else:
        logger.error("Failed to start agent")
        sys.exit(1)


if __name__ == "__main__":
    run()
