"""
Windows service implementation for StressSense Agent.
"""

import os
import sys
import time
import logging
import servicemanager
import win32event
import win32service
import win32serviceutil

from windows_agent.agent import StressAgent

# Configure logging
log_dir = os.path.expanduser('~/StressSense')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'service.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StressSenseService(win32serviceutil.ServiceFramework):
    """Windows Service for StressSense Agent."""
    
    _svc_name_ = "StressSenseService"
    _svc_display_name_ = "StressSense Detection Agent"
    _svc_description_ = "Monitors and detects employee stress levels using webcam analysis"
    
    def __init__(self, args):
        """Initialize the service."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.agent = None
        
        # Add current directory to path to ensure imports work
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
    
    def SvcStop(self):
        """Stop the service."""
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            
            logger.info("Service stop requested")
            
            # Stop the agent
            if self.agent:
                self.agent.stop()
        except Exception as e:
            logger.error(f"Error stopping service: {str(e)}", exc_info=True)
    
    def SvcDoRun(self):
        """Run the service."""
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            logger.info("Service starting")
            self.main()
        except Exception as e:
            logger.error(f"Error running service: {str(e)}", exc_info=True)
            servicemanager.LogErrorMsg(f"Error: {str(e)}")
    
    def main(self):
        """Main service function."""
        try:
            # Initialize and start the agent
            self.agent = StressAgent()
            if not self.agent.start():
                logger.error("Failed to start agent")
                return
                
            # Wait for service stop signal
            while True:
                # Check for stop signal
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
                # Sleep to reduce CPU usage
                time.sleep(1)
        except Exception as e:
            logger.error(f"Service main loop error: {str(e)}", exc_info=True)
        finally:
            # Ensure agent is stopped
            if self.agent:
                self.agent.stop()
            logger.info("Service stopped")


def run_service():
    """Run the service."""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(StressSenseService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(StressSenseService)
