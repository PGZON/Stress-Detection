import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import cv2
import json
import os
import sys
import requests
from datetime import datetime, timedelta
import threading
import schedule
from stress_analysis import analyze_image
import base64

# Configuration
CONFIG_FILE = "device_config.json"
BACKEND_URL = "http://localhost:8000"  # Change this to your backend URL
API_PREFIX = "/api/v1"
CAPTURE_INTERVAL_MINUTES = 30  # Change this to set the interval

class StressDetectionService(win32serviceutil.ServiceFramework):
    _svc_name_ = "StressDetectionService"
    _svc_display_name_ = "Stress Detection Service"
    _svc_description_ = "Background service for stress level detection"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._get_logger()
        self.stop_event = threading.Event()
        self.scheduler_thread = None

    def _get_logger(self):
        logger = logging.getLogger('[StressDetectionService]')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def SvcStop(self):
        self.logger.info('Stopping service...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        self.logger.info('Service started')
        self.main()

    def load_config(self):
        """Load device configuration"""
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        return None

    def capture_and_analyze(self):
        """Capture image from webcam and analyze stress"""
        try:
            self.logger.info("Starting stress detection cycle")

            # Load configuration
            config = self.load_config()
            if not config:
                self.logger.error("No device configuration found. Please run register_device.py first.")
                return

            # Capture image from webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.logger.error("Could not open webcam")
                return

            ret, frame = cap.read()
            cap.release()

            if not ret:
                self.logger.error("Failed to capture image from webcam")
                return

            # Convert to base64 for analysis
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # Analyze the image
            result = analyze_image(img_base64)

            if "error" in result:
                self.logger.warning(f"Analysis failed: {result['error']}")
                return

            self.logger.info(f"Analysis successful: {result['emotion']} -> {result['stress_level']}")

            # Prepare data for backend
            stress_data = {
                "device_id": config["device_id"],
                "employee_id": config["employee_id"],
                "emotion": result["emotion"],
                "stress_level": result["stress_level"],
                "confidence": result["confidence"],
                "timestamp": datetime.now().isoformat(),
                "face_quality": result.get("face_quality")
            }

            # Send to backend
            self.send_to_backend(stress_data, config["api_key"])

        except Exception as e:
            self.logger.error(f"Error in capture_and_analyze: {e}")

    def send_to_backend(self, data, api_key):
        """Send stress data to backend"""
        try:
            url = f"{BACKEND_URL}{API_PREFIX}/stress/record"
            headers = {
                "X-Device-Key": api_key,
                "Content-Type": "application/json"
            }

            self.logger.info(f"Sending stress data to backend: {data}")
            self.logger.info(f"Backend URL: {url}")
            self.logger.info(f"Headers: {headers}")

            response = requests.post(url, json=data, headers=headers, timeout=10)

            self.logger.info(f"Response status: {response.status_code}")
            self.logger.info(f"Response text: {response.text}")

            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Successfully sent stress data. Record ID: {result.get('record_id')}")
            else:
                self.logger.error(f"Failed to send data: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error sending data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in send_to_backend: {e}")

    def scheduler_worker(self):
        """Worker thread for scheduled tasks"""
        # Schedule the capture function
        schedule.every(CAPTURE_INTERVAL_MINUTES).minutes.do(self.capture_and_analyze)

        # Run initial capture
        self.capture_and_analyze()

        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def main(self):
        """Main service loop"""
        try:
            # Check if device is registered
            config = self.load_config()
            if not config:
                self.logger.error("Device not registered. Please run register_device.py first.")
                return

            self.logger.info(f"Service running for device: {config['device_id']}, employee: {config['employee_id']}")
            self.logger.info(f"Capture interval: {CAPTURE_INTERVAL_MINUTES} minutes")

            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self.scheduler_worker)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()

            # Wait for stop event
            while not self.stop_event.is_set():
                time.sleep(1)

            # Wait for scheduler thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)

        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(StressDetectionService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(StressDetectionService)