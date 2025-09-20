import win32serviceutil
import win32service
import sys
import os

def install_service():
    """Install the Windows service"""
    try:
        # Get the full path to the service script
        service_path = os.path.join(os.path.dirname(__file__), 'stress_detection_service.py')

        # Install the service
        win32serviceutil.InstallService(
            None,  # service name (uses class name)
            'StressDetectionService',  # display name
            'Stress Detection Service',  # description
            service_path,  # executable
            startType=win32service.SERVICE_AUTO_START
        )

        print("Service installed successfully!")
        print("You can start it from Windows Services or use 'python start_service.py'")

    except Exception as e:
        print(f"Error installing service: {e}")
        return False

    return True

def uninstall_service():
    """Uninstall the Windows service"""
    try:
        win32serviceutil.RemoveService('StressDetectionService')
        print("Service uninstalled successfully!")
    except Exception as e:
        print(f"Error uninstalling service: {e}")
        return False
    return True

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'uninstall':
            return uninstall_service()
        elif command == 'install':
            return install_service()
        else:
            print("Usage: python install_service.py [install|uninstall]")
            return False
    else:
        # Default to install
        return install_service()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)