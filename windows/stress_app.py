import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import subprocess
import threading
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import emotion stress mapping
try:
    from stress_analysis import EMOTION_STRESS_MAP
except ImportError:
    # Fallback mapping if import fails
    EMOTION_STRESS_MAP = {
        "happy": {"level": "Low", "min_confidence": 20},
        "neutral": {"level": "Low", "min_confidence": 25},
        "sad": {"level": "Medium", "min_confidence": 30},
        "angry": {"level": "Medium", "min_confidence": 30},
        "fear": {"level": "High", "min_confidence": 35},
        "disgust": {"level": "High", "min_confidence": 35},
        "surprise": {"level": "Medium", "min_confidence": 30}
    }

# Load environment variables
load_dotenv()

class StressDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StressSense - Employee Portal")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Configuration
        self.config_file = os.getenv("CONFIG_FILE", "device_config.json")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")

        # Current user session
        self.current_user = None
        self.access_token = None

        # Auto analysis timer
        self.auto_timer = None

        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initialize UI
        self.show_terms_conditions()

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_terms_conditions(self):
        """Show terms and conditions screen"""
        self.clear_frame()

        # Title
        title_label = ttk.Label(self.main_frame, text="Terms and Conditions",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Terms text
        terms_frame = ttk.Frame(self.main_frame)
        terms_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))

        terms_text = scrolledtext.ScrolledText(terms_frame, width=60, height=15, wrap=tk.WORD)
        terms_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        terms_content = """
STRESSSENSE EMPLOYEE STRESS DETECTION SYSTEM

TERMS AND CONDITIONS

1. PURPOSE
This application monitors employee stress levels through facial expression analysis to promote workplace wellness.

2. DATA COLLECTION
- Facial images are captured locally on your device
- Images are processed locally and immediately deleted
- Only stress analysis results are transmitted to the server
- No images or videos are stored or transmitted

3. PRIVACY PROTECTION
- All processing occurs on your local device
- Stress data is anonymized and aggregated
- Data is retained for 12 months and then anonymized
- You can request data deletion at any time

4. DEVICE REGISTRATION
- Each device must be registered to a specific employee
- Registration prevents data mixing between employees
- You can unregister your device at any time

5. SYSTEM REQUIREMENTS
- Windows 10/11 operating system
- Webcam access required
- Internet connection for data transmission
- Background service operation

6. USER RESPONSIBILITIES
- Ensure proper lighting for accurate detection
- Position yourself appropriately in camera view
- Keep webcam clean and functional
- Report any technical issues promptly

7. LIMITATIONS
- System provides stress level estimates only
- Not a substitute for professional medical advice
- Results may vary based on lighting and positioning
- System requires clear facial visibility

8. DATA USAGE
- Stress data helps management identify wellness trends
- Individual data remains confidential
- Aggregated data may be used for workplace improvements

9. TECHNICAL SUPPORT
- Contact your IT department for technical issues
- Service can be paused or uninstalled at any time

10. AGREEMENT
By accepting these terms, you agree to participate in workplace stress monitoring for wellness purposes.

Last updated: September 2025
        """

        terms_text.insert(tk.END, terms_content)
        terms_text.config(state=tk.DISABLED)

        # Accept checkbox
        self.accept_var = tk.BooleanVar()
        accept_check = ttk.Checkbutton(self.main_frame, text="I accept the terms and conditions",
                                      variable=self.accept_var)
        accept_check.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2)

        accept_btn = ttk.Button(button_frame, text="Accept & Continue",
                               command=self.on_terms_accepted)
        accept_btn.grid(row=0, column=0, padx=(0, 10))

        decline_btn = ttk.Button(button_frame, text="Decline & Exit",
                                command=self.on_terms_declined)
        decline_btn.grid(row=0, column=1)

    def on_terms_accepted(self):
        """Handle terms acceptance"""
        if not self.accept_var.get():
            messagebox.showerror("Error", "Please accept the terms and conditions to continue.")
            return

        # Check if device is already registered
        if self.load_config():
            self.show_main_menu()
        else:
            self.show_login()

    def on_terms_declined(self):
        """Handle terms decline"""
        if messagebox.askyesno("Confirm", "Are you sure you want to exit?"):
            self.root.quit()

    def show_login(self):
        """Show login screen"""
        self.clear_frame()

        # Title
        title_label = ttk.Label(self.main_frame, text="Login to StressSense",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Login form
        ttk.Label(self.main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.main_frame, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        login_btn = ttk.Button(button_frame, text="Login", command=self.do_login)
        login_btn.grid(row=0, column=0, padx=(0, 10))

        register_btn = ttk.Button(button_frame, text="Register New User", command=self.show_user_registration)
        register_btn.grid(row=0, column=1, padx=(0, 10))

        back_btn = ttk.Button(button_frame, text="Back", command=self.show_terms_conditions)
        back_btn.grid(row=0, column=2)

        # Status label
        self.login_status_var = tk.StringVar()
        status_label = ttk.Label(self.main_frame, textvariable=self.login_status_var, foreground="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))

    def do_login(self):
        """Perform login"""
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.login_status_var.set("Please enter both username and password.")
            return

        # Perform login request
        try:
            url = f"{self.backend_url}{self.api_prefix}/auth/login"
            data = {"username": username, "password": password}

            logger.info(f"[LOGIN] Sending login data: {data}")
            logger.info(f"[LOGIN] URL: {url}")

            response = requests.post(url, data=data)
            
            logger.info(f"[LOGIN] Response status: {response.status_code}")
            logger.info(f"[LOGIN] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            logger.info(f"[LOGIN] Login successful for user: {username}")
            
            self.current_user = result
            self.access_token = result.get("access_token")  # Store the access token

            self.login_status_var.set("Login successful!")
            self.root.after(1000, self.show_device_registration)

        except requests.exceptions.RequestException as e:
            logger.error(f"[LOGIN] Login failed: {str(e)}")
            self.login_status_var.set(f"Login failed: {str(e)}")
        except Exception as e:
            logger.error(f"[LOGIN] Error: {str(e)}")
            self.login_status_var.set(f"Error: {str(e)}")

    def show_user_registration(self):
        """Show user registration screen"""
        self.clear_frame()

        # Title
        title_label = ttk.Label(self.main_frame, text="Register New User",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Get device info
        device_info = self.get_device_info()

        # Device info display
        device_info_frame = ttk.LabelFrame(self.main_frame, text="Device Information", padding="10")
        device_info_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))

        device_info_text = f"Device Number: {device_info.get('device_number', 'Unknown')}\n"
        device_info_text += f"OS: {device_info.get('os', 'Unknown')}\n"
        device_info_text += f"OS Version: {device_info.get('os_version', 'Unknown')}\n"
        device_info_text += f"Architecture: {device_info.get('architecture', 'Unknown')}\n"
        device_info_text += f"Hostname: {device_info.get('hostname', 'Unknown')}\n"
        device_info_text += f"MAC Address: {device_info.get('mac_address', 'Unknown')}"

        device_info_label = ttk.Label(device_info_frame, text=device_info_text, justify=tk.LEFT)
        device_info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Registration form
        ttk.Label(self.main_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reg_username_var = tk.StringVar()
        username_entry = ttk.Entry(self.main_frame, textvariable=self.reg_username_var, width=30)
        username_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.reg_password_var = tk.StringVar()
        password_entry = ttk.Entry(self.main_frame, textvariable=self.reg_password_var, show="*", width=30)
        password_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Confirm Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.reg_confirm_password_var = tk.StringVar()
        confirm_entry = ttk.Entry(self.main_frame, textvariable=self.reg_confirm_password_var, show="*", width=30)
        confirm_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Full Name:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.reg_fullname_var = tk.StringVar()
        fullname_entry = ttk.Entry(self.main_frame, textvariable=self.reg_fullname_var, width=30)
        fullname_entry.grid(row=5, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Email:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.reg_email_var = tk.StringVar()
        email_entry = ttk.Entry(self.main_frame, textvariable=self.reg_email_var, width=30)
        email_entry.grid(row=6, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Employee ID:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.reg_employee_id_var = tk.StringVar()
        employee_entry = ttk.Entry(self.main_frame, textvariable=self.reg_employee_id_var, width=30)
        employee_entry.grid(row=7, column=1, pady=5, padx=(10, 0))

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        register_btn = ttk.Button(button_frame, text="Register", command=self.do_user_registration)
        register_btn.grid(row=0, column=0, padx=(0, 10))

        back_btn = ttk.Button(button_frame, text="Back to Login", command=self.show_login)
        back_btn.grid(row=0, column=1)

        # Status label
        self.reg_status_var = tk.StringVar()
        status_label = ttk.Label(self.main_frame, textvariable=self.reg_status_var, foreground="red")
        status_label.grid(row=9, column=0, columnspan=2, pady=(10, 0))

    def do_user_registration(self):
        """Perform user registration"""
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get()
        confirm_password = self.reg_confirm_password_var.get()
        fullname = self.reg_fullname_var.get().strip()
        email = self.reg_email_var.get().strip()
        employee_id = self.reg_employee_id_var.get().strip()

        # Validation
        if not all([username, password, confirm_password, fullname, email, employee_id]):
            self.reg_status_var.set("Please fill in all fields.")
            return

        if password != confirm_password:
            self.reg_status_var.set("Passwords do not match.")
            return

        if len(password) < 6:
            self.reg_status_var.set("Password must be at least 6 characters long.")
            return

        # Perform registration request
        try:
            url = f"{self.backend_url}{self.api_prefix}/auth/register"
            data = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "employee_id": employee_id,
                "role": "employee"
            }

            logger.info(f"[USER REGISTRATION] Sending registration data: {data}")
            logger.info(f"[USER REGISTRATION] URL: {url}")

            response = requests.post(url, json=data)
            
            logger.info(f"[USER REGISTRATION] Response status: {response.status_code}")
            logger.info(f"[USER REGISTRATION] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            self.current_user = result

            self.reg_status_var.set("Registration successful! Proceeding to device setup...")
            self.root.after(1000, self.show_device_registration)

        except requests.exceptions.RequestException as e:
            self.reg_status_var.set(f"Registration failed: {str(e)}")
        except Exception as e:
            self.reg_status_var.set(f"Error: {str(e)}")

    def show_device_registration(self):
        """Show device registration screen"""
        self.clear_frame()

        # Title
        title_label = ttk.Label(self.main_frame, text="Device Registration",
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Info
        info_text = f"Logged in as: {self.current_user.get('username', 'Unknown')}\n\n"
        info_text += "Please register this device for stress monitoring."

        info_label = ttk.Label(self.main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Get device info
        device_info = self.get_device_info()

        # Registration form
        ttk.Label(self.main_frame, text="Employee ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.employee_id_var = tk.StringVar()
        self.employee_id_var.set(self.current_user.get('employee_id', ''))
        employee_entry = ttk.Entry(self.main_frame, textvariable=self.employee_id_var, width=30)
        employee_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Device Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.device_name_var = tk.StringVar()
        self.device_name_var.set(f"{self.current_user.get('username', 'User')}'s Device")
        device_entry = ttk.Entry(self.main_frame, textvariable=self.device_name_var, width=30)
        device_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(self.main_frame, text="Device Number:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.device_number_var = tk.StringVar()
        self.device_number_var.set(device_info.get('device_number', ''))
        device_number_entry = ttk.Entry(self.main_frame, textvariable=self.device_number_var, width=30)
        device_number_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        # Device info display
        device_info_frame = ttk.LabelFrame(self.main_frame, text="Device Information", padding="10")
        device_info_frame.grid(row=5, column=0, columnspan=2, pady=(10, 20), sticky=(tk.W, tk.E))

        device_info_text = f"Device Name: {self.device_name_var.get()}\n"
        device_info_text += f"Device Number: {device_info.get('device_number', 'Unknown')}\n"
        device_info_text += f"OS: {device_info.get('os', 'Unknown')}\n"
        device_info_text += f"OS Version: {device_info.get('os_version', 'Unknown')}\n"
        device_info_text += f"Architecture: {device_info.get('architecture', 'Unknown')}\n"
        device_info_text += f"Hostname: {device_info.get('hostname', 'Unknown')}\n"
        device_info_text += f"MAC Address: {device_info.get('mac_address', 'Unknown')}"

        device_info_label = ttk.Label(device_info_frame, text=device_info_text, justify=tk.LEFT)
        device_info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Store reference to device info label for updates
        self.device_info_label = device_info_label

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        register_btn = ttk.Button(button_frame, text="Register Device", command=self.do_register_device)
        register_btn.grid(row=0, column=0, padx=(0, 10))

        logout_btn = ttk.Button(button_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1)

        # Status label
        self.register_status_var = tk.StringVar()
        status_label = ttk.Label(self.main_frame, textvariable=self.register_status_var, foreground="red")
        status_label.grid(row=7, column=0, columnspan=2, pady=(10, 0))

    def do_register_device(self):
        """Register the device"""
        employee_id = self.employee_id_var.get().strip()
        device_name = self.device_name_var.get().strip()
        device_number = self.device_number_var.get().strip()

        if not employee_id:
            self.register_status_var.set("Please enter an Employee ID.")
            return

        if not device_name:
            device_name = f"{self.current_user.get('username', 'User')}'s Device"

        if not device_number:
            device_number = self.get_device_info().get('device_number', 'Unknown')

        # Get device info
        device_info = self.get_device_info()

        # Register device
        try:
            url = f"{self.backend_url}{self.api_prefix}/devices/register"
            data = {
                "employee_id": employee_id,
                "device_name": device_name,
                "device_number": device_number,
                "device_type": "windows_agent",
                "device_info": {
                    "os": device_info.get('os', 'Unknown'),
                    "os_version": device_info.get('os_version', 'Unknown'),
                    "architecture": device_info.get('architecture', 'Unknown'),
                    "hostname": device_info.get('hostname', 'Unknown'),
                    "mac_address": device_info.get('mac_address', 'Unknown')
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            logger.info(f"[DEVICE REGISTRATION] Sending registration data: {data}")
            logger.info(f"[DEVICE REGISTRATION] URL: {url}")
            logger.info(f"[DEVICE REGISTRATION] Headers: {headers}")

            response = requests.post(url, json=data, headers=headers)
            
            logger.info(f"[DEVICE REGISTRATION] Response status: {response.status_code}")
            logger.info(f"[DEVICE REGISTRATION] Response text: {response.text}")
            
            response.raise_for_status()

            result = response.json()
            logger.info(f"[DEVICE REGISTRATION] Registration successful: {result}")

            # Save configuration
            config = {
                "device_id": result['device_id'],
                "api_key": result['api_key'],
                "employee_id": employee_id,
                "device_name": device_name,
                "device_number": device_number,
                "username": self.current_user.get('username'),
                "user_id": self.current_user.get('user_id'),
                "role": "employee",
                "registered_at": datetime.now().isoformat(),
                "backend_url": self.backend_url
            }
            self.save_config(config)

            self.register_status_var.set("Device registered successfully!")
            self.root.after(1000, self.show_main_menu)

        except requests.exceptions.RequestException as e:
            self.register_status_var.set(f"Registration failed: {str(e)}")
        except Exception as e:
            self.register_status_var.set(f"Error: {str(e)}")

    def get_device_info(self):
        """Get device information"""
        try:
            import platform
            import socket
            import uuid

            device_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "device_number": str(uuid.getnode()),  # MAC address as unique identifier
                "mac_address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
            }
            return device_info
        except Exception as e:
            return {
                "os": "Unknown",
                "os_version": "Unknown",
                "architecture": "Unknown",
                "hostname": "Unknown",
                "device_number": "Unknown",
                "mac_address": "Unknown"
            }

    def update_device_info_display(self):
        """Update the device information display"""
        try:
            device_info = self.get_device_info()
            device_info_text = f"Device Name: {self.device_name_var.get()}\n"
            device_info_text += f"Device Number: {self.device_number_var.get() or device_info.get('device_number', 'Unknown')}\n"
            device_info_text += f"OS: {device_info.get('os', 'Unknown')}\n"
            device_info_text += f"OS Version: {device_info.get('os_version', 'Unknown')}\n"
            device_info_text += f"Architecture: {device_info.get('architecture', 'Unknown')}\n"
            device_info_text += f"Hostname: {device_info.get('hostname', 'Unknown')}\n"
            device_info_text += f"MAC Address: {device_info.get('mac_address', 'Unknown')}"

            if hasattr(self, 'device_info_label'):
                self.device_info_label.config(text=device_info_text)
        except Exception as e:
            print(f"Error updating device info display: {e}")

    def show_main_menu(self):
        """Show main menu"""
        self.clear_frame()

        # Load config
        config = self.load_config()

        # Title
        title_label = ttk.Label(self.main_frame, text="StressSense Control Panel",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Status info
        if config:
            status_text = f"User: {config.get('username', 'Unknown')}\n"
            status_text += f"Device: {config.get('device_name', 'Unknown')}\n"
            status_text += f"Device Number: {config.get('device_number', 'Unknown')}\n"
            status_text += f"Employee ID: {config.get('employee_id', 'Unknown')}\n"
            status_text += f"Status: {'Registered' if config else 'Not Registered'}"
        else:
            status_text = "Status: Not Registered"

        status_label = ttk.Label(self.main_frame, text=status_text, justify=tk.LEFT)
        status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Buttons
        if config:
            # Service control buttons
            service_frame = ttk.LabelFrame(self.main_frame, text="Service Control", padding="10")
            service_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))

            install_btn = ttk.Button(service_frame, text="Install Service", command=self.install_service)
            install_btn.grid(row=0, column=0, padx=(0, 10), pady=5)

            start_btn = ttk.Button(service_frame, text="Start Service", command=self.start_service)
            start_btn.grid(row=0, column=1, padx=(0, 10), pady=5)

            stop_btn = ttk.Button(service_frame, text="Stop Service", command=self.stop_service)
            stop_btn.grid(row=0, column=2, padx=(0, 10), pady=5)

            uninstall_btn = ttk.Button(service_frame, text="Uninstall Service", command=self.uninstall_service)
            uninstall_btn.grid(row=0, column=3, pady=5)

            # Test button
            test_frame = ttk.LabelFrame(self.main_frame, text="Testing", padding="10")
            test_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))

            test_btn = ttk.Button(test_frame, text="Test Stress Detection", command=self.test_detection)
            test_btn.grid(row=0, column=0, padx=(0, 10))

            # Status label
            self.service_status_var = tk.StringVar()
            self.service_status_var.set("Ready")
            status_label = ttk.Label(test_frame, textvariable=self.service_status_var)
            status_label.grid(row=0, column=1, padx=(10, 0))

            bottom_row = 4

        # Bottom buttons
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.grid(row=bottom_row, column=0, columnspan=2, pady=(20, 0))

        if config:
            re_register_btn = ttk.Button(bottom_frame, text="Re-register Device", command=self.re_register)
            re_register_btn.grid(row=0, column=0, padx=(0, 10))

        logout_btn = ttk.Button(bottom_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1)

        # Start auto analysis if device is registered
        if config and not self.auto_timer:
            self.start_auto_analysis()

    def install_service(self):
        """Install the Windows service"""
        try:
            result = subprocess.run([sys.executable, "install_service.py"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service installed successfully!")
            else:
                messagebox.showerror("Error", f"Failed to install service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error installing service: {str(e)}")

    def start_service(self):
        """Start the Windows service"""
        try:
            result = subprocess.run([sys.executable, "start_service.py"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service started successfully!")
            else:
                messagebox.showerror("Error", f"Failed to start service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error starting service: {str(e)}")

    def stop_service(self):
        """Stop the Windows service"""
        try:
            result = subprocess.run([sys.executable, "start_service.py", "stop"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service stopped successfully!")
            else:
                messagebox.showerror("Error", f"Failed to stop service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping service: {str(e)}")

    def uninstall_service(self):
        """Uninstall the Windows service"""
        try:
            result = subprocess.run([sys.executable, "install_service.py", "uninstall"],
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                messagebox.showinfo("Success", "Service uninstalled successfully!")
            else:
                messagebox.showerror("Error", f"Failed to uninstall service:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Error uninstalling service: {str(e)}")

    def test_detection(self):
        """Test stress detection and send to backend"""
        config = self.load_config()
        if not config:
            self.service_status_var.set("Device not registered")
            return

        self.service_status_var.set("Testing...")

        def run_test():
            try:
                # Import here to avoid issues if not installed
                try:
                    from stress_analysis import analyze_image
                except ImportError as import_error:
                    logger.error(f"[TEST DETECTION] Failed to import analyze_image: {str(import_error)}")
                    self.service_status_var.set("Analysis module not available")
                    return
                    
                import cv2
                import base64
                from datetime import datetime

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.error("[IMAGE CAPTURE] Failed to open webcam")
                    self.service_status_var.set("No webcam found")
                    return

                # Try multiple capture attempts
                ret = False
                frame = None
                for attempt in range(3):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[IMAGE CAPTURE] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)  # Wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.error("[IMAGE CAPTURE] Failed to capture image after 3 attempts")
                    self.service_status_var.set("Failed to capture image")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.error(f"[IMAGE CAPTURE] Invalid frame dimensions: {frame.shape}")
                    self.service_status_var.set("Invalid image captured")
                    return

                logger.info(f"[IMAGE CAPTURE] Successfully captured image with shape: {frame.shape}")

                # Convert to base64 with error handling
                try:
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    if buffer is None or buffer.size == 0:
                        logger.error("[IMAGE CAPTURE] Failed to encode image to JPEG")
                        self.service_status_var.set("Failed to encode image")
                        return
                    
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    if not img_base64:
                        logger.error("[IMAGE CAPTURE] Base64 encoding resulted in empty string")
                        self.service_status_var.set("Failed to encode image data")
                        return
                        
                except Exception as encode_error:
                    logger.error(f"[IMAGE CAPTURE] Error encoding image: {str(encode_error)}")
                    self.service_status_var.set("Failed to process image")
                    return

                # Analyze locally
                result = analyze_image(img_base64)

                if "error" in result:
                    self.service_status_var.set(f"Error: {result['error']}")
                    return

                # Show local result first
                emotion = result.get('emotion', 'Unknown')
                stress_level = result.get('stress_level', 'Unknown')
                confidence = result.get('confidence', 0)
                local_result = f"Detected: {emotion} -> {stress_level} ({confidence:.1f}%)"

                logger.info(f"[LOCAL ANALYSIS] Result: {local_result}")
                self.service_status_var.set(local_result)

                # Send to backend
                logger.info("[BACKEND] Starting backend submission...")
                try:
                    url = f"{self.backend_url}{self.api_prefix}/stress/record"
                    api_key = config.get('api_key')
                    logger.info(f"[BACKEND] Using API key: {api_key[:8]}...")
                    headers = {
                        "X-Device-Key": api_key,
                        "Content-Type": "application/json"
                    }

                    # Map emotion to API enum format
                    emotion_map = {
                        'angry': 'angry',
                        'disgusted': 'disgust',
                        'fearful': 'fear',
                        'happy': 'happy',
                        'neutral': 'neutral',
                        'sad': 'sad',
                        'surprised': 'surprise'
                    }

                    api_emotion = emotion_map.get(emotion, 'neutral')

                    # Prepare submission data
                    submission_data = {
                        "emotion": api_emotion,
                        "stress_level": stress_level,
                        "confidence": float(confidence * 100),  # Convert to 0-100 scale
                        "timestamp": datetime.now().isoformat(),
                        "face_quality": result.get('face_quality')
                    }

                    print(f"[FRONTEND] Sending stress data to backend: {submission_data}")
                    print(f"[FRONTEND] URL: {url}")
                    print(f"[FRONTEND] Headers: {headers}")

                    logger.info(f"[STRESS SUBMISSION] Sending stress data: {submission_data}")
                    logger.info(f"[STRESS SUBMISSION] URL: {url}")
                    logger.info(f"[STRESS SUBMISSION] Headers: {headers}")

                    response = requests.post(url, json=submission_data, headers=headers)
                    print(f"[FRONTEND] Response status: {response.status_code}")
                    print(f"[FRONTEND] Response text: {response.text}")
                    
                    logger.info(f"[STRESS SUBMISSION] Response status: {response.status_code}")
                    logger.info(f"[STRESS SUBMISSION] Response text: {response.text}")
                    
                    response.raise_for_status()

                    backend_result = response.json()
                    record_id = backend_result.get('record_id', 'Unknown')

                    print(f"[FRONTEND] Successfully saved record: {record_id}")
                    logger.info(f"[STRESS SUBMISSION] Successfully saved record: {record_id}")
                    self.service_status_var.set(f"{local_result} | Saved: {record_id}")

                except requests.exceptions.RequestException as e:
                    print(f"[FRONTEND] Backend request failed: {str(e)}")
                    logger.error(f"[STRESS SUBMISSION] Backend request failed: {str(e)}")
                    self.service_status_var.set(f"{local_result} | Backend Error: {str(e)}")
                except Exception as e:
                    print(f"[FRONTEND] Save error: {str(e)}")
                    self.service_status_var.set(f"{local_result} | Save Error: {str(e)}")

            except Exception as e:
                self.service_status_var.set(f"Error: {str(e)}")

        # Run in thread to avoid blocking UI
        threading.Thread(target=run_test, daemon=True).start()

    def re_register(self):
        """Re-register device"""
        if messagebox.askyesno("Confirm", "This will unregister the current device. Continue?"):
            # Delete config
            config_path = os.path.join(os.path.dirname(__file__), self.config_file)
            if os.path.exists(config_path):
                os.remove(config_path)

            # Go back to login
            self.current_user = None
            self.access_token = None
            self.show_login()

    def logout(self):
        """Logout user"""
        # Cancel auto analysis timer
        if self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = None
        
        # Cancel remote check timer
        if hasattr(self, 'remote_timer') and self.remote_timer:
            self.remote_timer.cancel()
            self.remote_timer = None
        
        self.current_user = None
        self.access_token = None
        self.show_terms_conditions()

    def load_config(self):
        """Load device configuration"""
        config_path = os.path.join(os.path.dirname(__file__), self.config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_config(self, config):
        """Save device configuration"""
        config_path = os.path.join(os.path.dirname(__file__), self.config_file)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def start_auto_analysis(self):
        """Start automatic stress analysis every 2 minutes (dev mode)"""
        if hasattr(self, 'auto_timer') and self.auto_timer:
            self.auto_timer.cancel()

        self.auto_timer = threading.Timer(120, self.run_auto_analysis)  # 120 seconds = 2 minutes (dev mode)
        self.auto_timer.start()
        logger.info("[AUTO ANALYSIS] Started automatic stress analysis (every 2 minutes - dev mode)")

        # Also start checking for remote stress requests
        self.start_remote_check_timer()

    def start_remote_check_timer(self):
        """Start timer to check for remote stress check requests"""
        if hasattr(self, 'remote_timer') and self.remote_timer:
            self.remote_timer.cancel()

        # Use shorter interval for more responsive checking (30 seconds in dev mode)
        check_interval = 30  # 30 seconds for dev mode
        self.remote_timer = threading.Timer(check_interval, self.check_remote_stress_requests)
        self.remote_timer.start()
        logger.info(f"[REMOTE CHECK] Started checking for remote stress requests (every {check_interval} seconds - dev mode)")

    def check_remote_stress_requests(self):
        """Check for pending remote stress check requests"""
        config = self.load_config()
        if not config:
            logger.warning("[REMOTE CHECK] Device not registered, skipping remote check")
            self.start_remote_check_timer()  # Still restart timer
            return

        try:
            url = f"{self.backend_url}{self.api_prefix}/stress/remote-check/{config.get('employee_id')}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            logger.debug(f"[REMOTE CHECK] Checking for remote requests: {url}")
            response = requests.get(url, headers=headers, timeout=10)  # Add timeout

            if response.status_code == 200:
                request_data = response.json()
                if request_data.get('pending_request'):
                    logger.info("[REMOTE CHECK] Found pending remote stress check request - processing immediately")
                    # Run stress detection for remote request
                    self.run_remote_stress_check(request_data)
                    # After processing, restart timer with normal interval
                    self.start_remote_check_timer()
                else:
                    logger.debug("[REMOTE CHECK] No pending requests")
                    self.start_remote_check_timer()
            elif response.status_code == 401:
                logger.warning("[REMOTE CHECK] Authentication failed - token may be expired")
                self.start_remote_check_timer()
            elif response.status_code == 404:
                logger.warning("[REMOTE CHECK] Remote check endpoint not found - backend may need restart")
                self.start_remote_check_timer()
            else:
                logger.warning(f"[REMOTE CHECK] Failed to check remote requests: HTTP {response.status_code}")
                self.start_remote_check_timer()

        except requests.exceptions.Timeout:
            logger.warning("[REMOTE CHECK] Request timed out")
            self.start_remote_check_timer()
        except requests.exceptions.ConnectionError:
            logger.warning("[REMOTE CHECK] Connection error - backend may be down")
            self.start_remote_check_timer()
        except Exception as e:
            logger.error(f"[REMOTE CHECK] Error checking remote requests: {str(e)}")
            self.start_remote_check_timer()

    def run_remote_stress_check(self, request_data):
        """Run stress detection for remote request"""
        logger.info("[REMOTE STRESS] Running remote stress check")

        def run_check():
            try:
                # Import here to avoid issues if not installed
                try:
                    from stress_analysis import analyze_image, analyze_image_array
                except ImportError as import_error:
                    logger.error(f"[REMOTE STRESS] Failed to import stress_analysis: {str(import_error)}")
                    return
                import cv2
                from datetime import datetime

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.warning("[REMOTE STRESS] No webcam found")
                    return

                # Try multiple capture attempts
                ret = False
                frame = None
                for attempt in range(3):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[REMOTE STRESS] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)  # Wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.warning("[REMOTE STRESS] Failed to capture image after 3 attempts")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.warning(f"[REMOTE STRESS] Invalid frame dimensions: {frame.shape}")
                    return

                logger.info(f"[REMOTE STRESS] Successfully captured image with shape: {frame.shape}")

                # Analyze stress (no need to convert to base64 for local analysis)
                result = analyze_image_array(frame)

                logger.info(f"[REMOTE STRESS] Analysis result: {result}")
                if result:
                    if "error" in result:
                        logger.warning(f"[REMOTE STRESS] Analysis returned error: {result['error']}")
                    confidence = result.get('confidence', 0)
                    emotion = result.get('emotion', 'unknown')
                    logger.info(f"[REMOTE STRESS] Confidence: {confidence} (type: {type(confidence)}), Emotion: {emotion}")
                    emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25})
                    logger.info(f"[REMOTE STRESS] Required confidence for {emotion}: {emotion_config['min_confidence']}%")

                # Use emotion-specific confidence threshold
                emotion = result.get('emotion', '') if result else ''
                emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25})
                min_confidence = emotion_config["min_confidence"] / 100.0
                
                confidence_val = float(result.get('confidence', 0)) if result else 0.0
                should_submit = confidence_val > min_confidence
                
                logger.info(f"[REMOTE STRESS] Emotion: {emotion}, Confidence: {confidence_val:.3f}, Min required: {min_confidence:.3f} ({emotion_config['min_confidence']}%), Should submit: {should_submit}")
                
                if result and "error" not in result and confidence_val > min_confidence:
                    # Submit to backend with remote request info
                    logger.info("[REMOTE STRESS] Starting backend submission for high confidence result")
                    config = self.load_config()
                    if config:
                        url = f"{self.backend_url}{self.api_prefix}/stress/remote-submit"
                        
                        # Map emotion to API enum format
                        emotion = result.get('emotion')
                        emotion_map = {
                            'angry': 'angry',
                            'disgusted': 'disgust',
                            'fearful': 'fear',
                            'happy': 'happy',
                            'neutral': 'neutral',
                            'sad': 'sad',
                            'surprised': 'surprise'
                        }
                        api_emotion = emotion_map.get(emotion, 'neutral')
                        
                        logger.info(f"[REMOTE STRESS] Original emotion: {emotion}, Mapped emotion: {api_emotion}")
                        
                        data = {
                            "stress_level": result.get('stress_level'),
                            "emotion": api_emotion,
                            "confidence": result.get('confidence', 0) * 100,  # Convert to 0-100 scale
                            "request_id": request_data.get('request_id'),
                            "remote_request": True
                        }

                        headers = {
                            "X-Device-Key": config.get('api_key'),
                            "Content-Type": "application/json"
                        }

                        logger.info(f"[REMOTE STRESS] Using API key: {config.get('api_key')[:8]}...")
                        logger.info(f"[REMOTE STRESS] Submitting to: {url}")

                        response = requests.post(url, json=data, headers=headers)
                        status_code = response.status_code
                        if status_code in [200, 201] or str(status_code) in ["200", "201"]:
                            logger.info(f"[REMOTE STRESS] Remote stress data submitted: {result}")
                            # Update status if possible
                            if hasattr(self, 'service_status_var'):
                                self.service_status_var.set("Remote stress check completed")
                        else:
                            logger.warning(f"[REMOTE STRESS] Failed to submit remote data: {status_code} (type: {type(status_code)})")

            except Exception as e:
                logger.error(f"[REMOTE STRESS] Error: {str(e)}")

        # Run in background thread
        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()

    def run_auto_analysis(self):
        """Run automatic stress analysis"""
        config = self.load_config()
        if not config:
            logger.warning("[AUTO ANALYSIS] Device not registered, skipping analysis")
            return

        logger.info("[AUTO ANALYSIS] Running automatic stress analysis")
        # Run the same test detection logic
        self.test_detection_background()

        # Restart timer
        self.start_auto_analysis()

    def test_detection_background(self):
        """Run stress detection in background"""
        def run_test():
            try:
                # Import here to avoid issues if not installed
                try:
                    from stress_analysis import analyze_image, analyze_image_array
                except ImportError as import_error:
                    logger.error(f"[AUTO ANALYSIS] Failed to import stress_analysis: {str(import_error)}")
                    return
                    
                import cv2
                import base64
                from datetime import datetime

                # Capture image with better error handling
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    logger.warning("[AUTO ANALYSIS] No webcam found")
                    return

                # Try multiple capture attempts
                ret = False
                frame = None
                for attempt in range(3):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        break
                    logger.warning(f"[AUTO ANALYSIS] Capture attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)  # Wait before retry
                
                cap.release()

                if not ret or frame is None:
                    logger.warning("[AUTO ANALYSIS] Failed to capture image after 3 attempts")
                    return

                # Validate captured frame
                if frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
                    logger.warning(f"[AUTO ANALYSIS] Invalid frame dimensions: {frame.shape}")
                    return

                logger.debug(f"[AUTO ANALYSIS] Successfully captured image with shape: {frame.shape}")

                # Analyze stress (no need to convert to base64 for local analysis)
                result = analyze_image_array(frame)

                logger.info(f"[AUTO ANALYSIS] Analysis result: {result}")
                if result:
                    if "error" in result:
                        logger.warning(f"[AUTO ANALYSIS] Analysis returned error: {result['error']}")
                    confidence = result.get('confidence', 0)
                    emotion = result.get('emotion', 'unknown')
                    logger.info(f"[AUTO ANALYSIS] Confidence: {confidence} (type: {type(confidence)}), Emotion: {emotion}")
                    emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25})
                    logger.info(f"[AUTO ANALYSIS] Required confidence for {emotion}: {emotion_config['min_confidence']}%")

                # Use emotion-specific confidence threshold instead of fixed 0.5
                emotion = result.get('emotion', '') if result else ''
                emotion_config = EMOTION_STRESS_MAP.get(emotion, {"min_confidence": 25})
                min_confidence = emotion_config["min_confidence"] / 100.0  # Convert to decimal
                
                confidence_val = float(result.get('confidence', 0)) if result else 0.0
                should_submit = confidence_val > min_confidence
                
                logger.info(f"[AUTO ANALYSIS] Emotion: {emotion}, Confidence: {confidence_val:.3f}, Min required: {min_confidence:.3f} ({emotion_config['min_confidence']}%), Should submit: {should_submit}")
                
                if result and "error" not in result and confidence_val > min_confidence:
                    # Submit to backend
                    logger.info("[AUTO ANALYSIS] Starting backend submission for high confidence result")
                    config = self.load_config()
                    if config:
                        url = f"{self.backend_url}{self.api_prefix}/stress/record"
                        api_key = config.get('api_key')
                        logger.info(f"[AUTO ANALYSIS] Using API key: {api_key[:8]}...")
                        
                        # Map emotion to API enum format
                        emotion = result.get('emotion')
                        emotion_map = {
                            'angry': 'angry',
                            'disgusted': 'disgust',
                            'fearful': 'fear',
                            'happy': 'happy',
                            'neutral': 'neutral',
                            'sad': 'sad',
                            'surprised': 'surprise'
                        }
                        api_emotion = emotion_map.get(emotion, 'neutral')
                        logger.info(f"[AUTO ANALYSIS] Original emotion: {emotion}, Mapped emotion: {api_emotion}")
                        
                        headers = {
                            "X-Device-Key": api_key,
                            "Content-Type": "application/json"
                        }
                        data = {
                            "emotion": api_emotion,
                            "stress_level": result.get('stress_level'),
                            "confidence": result.get('confidence', 0) * 100,  # Convert to 0-100 scale
                            "timestamp": datetime.now().isoformat(),
                            "face_quality": result.get('face_quality')
                        }

                        response = requests.post(url, json=data, headers=headers)
                        status_code = response.status_code
                        if status_code in [200, 201] or str(status_code) in ["200", "201"]:
                            logger.info(f"[AUTO ANALYSIS] Stress data submitted: {result}")
                        else:
                            logger.warning(f"[AUTO ANALYSIS] Failed to submit: {status_code} (type: {type(status_code)})")

            except Exception as e:
                logger.error(f"[AUTO ANALYSIS] Error: {str(e)}")

        # Run in background thread
        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = StressDetectionApp(root)
    
    # Start automatic analysis if device is registered
    config = app.load_config()
    if config:
        app.start_auto_analysis()
    
    # Handle app closing
    def on_closing():
        if app.auto_timer:
            app.auto_timer.cancel()
        if hasattr(app, 'remote_timer') and app.remote_timer:
            app.remote_timer.cancel()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()