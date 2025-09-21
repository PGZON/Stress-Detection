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
    ('stress_detection_service.py', '.'),
    ('.env', '.'),
    ('icon.ico', '.'),
]

# Add logs directory if it exists
logs_dir = os.path.join(current_dir, 'logs')
if os.path.exists(logs_dir):
    data_files.append(('logs', 'logs'))

# Define hidden imports
hidden_imports = [
    # Core Python modules
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.filedialog',
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

    # Third-party packages
    'requests',
    'dotenv',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
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
    'tensorflow.keras.preprocessing.image',
    'tensorflow.keras.applications',
    'tensorflow.keras.optimizers',
    'tensorflow.keras.losses',
    'tensorflow.keras.metrics',
    'tensorflow.keras.callbacks',
    'tensorflow.keras.backend',
    'tensorflow.python',
    'tensorflow.python.keras',
    'tensorflow.python.keras.models',
    'tensorflow.python.keras.utils',
    'tensorflow.python.keras.layers',
    'tensorflow.python.keras.preprocessing',
    'tensorflow.python.keras.preprocessing.image',
    'tensorflow.python.tools',
    'tensorflow.core',
    'tensorflow.core.framework',
    'tensorflow.core.protobuf',
    'tensorflow.compiler',
    'tensorflow.compiler.xla',
    'tensorflow.compiler.tf2xla',
    'tensorflow.lite',
    'tensorflow.lite.python',
    'tensorflow.estimator',
    'tensorflow.estimator.api',
    'tensorflow.feature_column',
    'tensorflow.saved_model',
    'tensorflow.saved_model.builder',
    'tensorflow.saved_model.signature_constants',
    'tensorflow.saved_model.tag_constants',
    'tensorflow.saved_model.utils',
    'tensorflow.summary',
    'tensorflow.train',
    'tensorflow.train.queue_runner',
    'tensorflow.data',
    'tensorflow.data.experimental',
    'tensorflow.io',
    'tensorflow.io.gfile',
    'tensorflow.math',
    'tensorflow.nn',
    'tensorflow.ops',
    'tensorflow.random',
    'tensorflow.strings',
    'tensorflow.sparse',
    'tensorflow.lookup',
    'tensorflow.experimental',
    'tensorflow.experimental.numpy',
    'tensorflow.compat',
    'tensorflow.compat.v1',
    'tensorflow.compat.v2',
    'keras',
    'keras.api',
    'keras.api.keras',
    'keras.api.keras.models',
    'keras.api.keras.layers',
    'keras.api.keras.utils',
    'keras.api.keras.preprocessing',
    'keras.api.keras.preprocessing.image',
    'keras.models',
    'keras.layers',
    'keras.utils',
    'keras.preprocessing',
    'keras.preprocessing.image',
    'keras.applications',
    'keras.optimizers',
    'keras.losses',
    'keras.metrics',
    'keras.callbacks',
    'keras.backend',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'schedule',
    'ttkthemes',
    'typing',
    'collections.abc',

    # Application modules - ALL Python files
    'stress_analysis',
    'stress_client',
    'register_device',
    'start_service',
    'install_service',
    'stress_app',
    'stress_detection_service',

    # Windows-specific modules
    'win32api',
    'win32con',
    'win32serviceutil',
    'win32service',
    'win32event',
    'servicemanager',
    'socket',
]

# Define binaries (DLLs, etc.)
binaries = []

# Define excludes
excludes = [
    'tkinter.test',
    'test',
    'unittest',
    'pydoc',
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
    ['stress_app.py', 'stress_analysis.py','stress_client.py'],
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
    name='StressSense',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)