# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

# Define data files to include
data_files = [
    ('stress_cnn_model.h5', '.'),
    ('stress_analysis.py', '.'),
    ('stress_client.py', '.'),
    ('register_device.py', '.'),
    ('start_service.py', '.'),
    ('install_service.py', '.'),
    ('.env', '.'),
    ('icon.ico', '.'),
]

# Add logs directory if it exists
logs_dir = os.path.join(current_dir, 'logs')
if os.path.exists(logs_dir):
    data_files.append(('logs', 'logs'))

# Define hidden imports for Windows service
hidden_imports = [
    # Core Python modules
    'json',
    'os',
    'sys',
    'subprocess',
    'threading',
    'time',
    'datetime',
    'platform',
    'uuid',
    'base64',
    'logging',
    'logging.handlers',

    # Windows service modules
    'win32api',
    'win32con',
    'win32serviceutil',
    'win32service',
    'win32event',
    'servicemanager',
    'socket',

    # Third-party packages
    'requests',
    'dotenv',
    'cv2',
    'cv2.cv2',
    'numpy',
    'numpy.core',
    'tensorflow',
    'tensorflow.keras',
    'tensorflow.keras.models',
    'tensorflow.keras.utils',
    'tensorflow.keras.layers',
    'tensorflow.keras.preprocessing',
    'keras',
    'PIL',
    'PIL.Image',
    'schedule',
    'typing',

    # Application modules - ALL Python files
    'stress_analysis',
    'stress_client',
    'register_device',
    'start_service',
    'install_service',
    'stress_app',
    'stress_detection_service',

# Define binaries (DLLs, etc.)
binaries = []

# Define excludes
excludes = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.filedialog',
    'tkinter.test',
    'test',
    'unittest',
    'pydoc',
    'ttkthemes',
    # TensorFlow optimizations - exclude unused components
    'tensorflow.compiler',
    'tensorflow.lite',
    'tensorflow.python.debug',
    'tensorflow.python.tools',
    'tensorflow.contrib',
    # Other large unused packages
    'matplotlib',
    'scipy',
    'pandas',
    'sklearn',
    'jupyter',
    'notebook',
    'ipykernel',
]

a = Analysis(
    ['stress_detection_service.py'],
    pathex=[current_dir],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StressDetectionService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Service needs console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)