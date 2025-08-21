"""
Setup script for creating a standalone executable with PyInstaller.
"""

import sys
import os
import subprocess

# Add resources directory
resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
os.makedirs(resources_dir, exist_ok=True)

# Ensure we have the icon first
from assets.create_icon import create_icon
icon_path = create_icon()

# Define PyInstaller arguments for Agent
agent_args = [
    '--name=StressSenseAgent',
    '--onefile',
    '--windowed',  # No console window in normal operation
    '--add-data=resources;resources',  # Include resources folder
    '--add-data=assets;assets',  # Include assets folder
    '--hidden-import=cv2',
    '--hidden-import=deepface',
    '--hidden-import=numpy',
    '--hidden-import=requests',
    '--hidden-import=win32api',
    '--hidden-import=win32security',
    '--hidden-import=win32event',
    '--hidden-import=win32service',
    '--hidden-import=win32serviceutil',
    '--hidden-import=servicemanager',
    '--hidden-import=pywintypes',
    f'--icon={icon_path}',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '__main__.py')
]

# Define PyInstaller arguments for Wellness Assistant
wellness_args = [
    '--name=StressSenseWellness',
    '--onefile',
    '--windowed',  # No console window in normal operation
    '--add-data=assets;assets',  # Include assets folder
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtChart',
    '--hidden-import=PyQt5.sip',
    '--hidden-import=sqlite3',
    '--hidden-import=deepface',
    '--hidden-import=numpy',
    '--hidden-import=requests',
    f'--icon={icon_path}',
    '--add-binary={}".\\__main__.py --wellness";.'.format(sys.executable),
]

# Run PyInstaller for Agent
print("Building StressSenseAgent executable...")
subprocess.run([sys.executable, '-m', 'PyInstaller'] + agent_args, check=True)

# Run PyInstaller for Wellness Assistant using spec file
print("Building StressSenseWellness executable...")
subprocess.run([sys.executable, '-m', 'PyInstaller', 'wellness.spec'], check=True)

print("Build completed.")
