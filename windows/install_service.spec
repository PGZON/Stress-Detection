# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(SPEC))

# Define data files to include
data_files = []

# Define hidden imports for service installer
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
    'logging',

    # Windows service modules
    'win32api',
    'win32con',
    'win32serviceutil',
    'win32service',
    'win32event',
    'servicemanager',
    'socket',

    # Application modules - ALL Python files
    'stress_analysis',
    'stress_client',
    'register_device',
    'start_service',
    'install_service',
    'stress_app',
    'stress_detection_service',
]

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
    'tensorflow',
    'tensorflow.keras',
    'tensorflow.keras.models',
    'tensorflow.keras.utils',
    'tensorflow.keras.layers',
    'tensorflow.keras.preprocessing',
    'keras',
    'cv2',
    'cv2.cv2',
    'numpy',
    'numpy.core',
    'PIL',
    'PIL.Image',
    'requests',
    'dotenv',
    'typing',
]

a = Analysis(
    ['install_service.py'],
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
    name='install_service',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)