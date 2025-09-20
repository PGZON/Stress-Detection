# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['stress_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('stress_cnn_model.h5', '.'),
        ('stress_analysis.py', '.'),
        ('register_device.py', '.'),
        ('stress_detection_service.py', '.'),
        ('install_service.py', '.'),
        ('start_service.py', '.'),
        ('license.txt', '.'),
    ],
    hiddenimports=[
        'tensorflow',
        'tensorflow.keras',
        'tensorflow.keras.models',
        'tensorflow.keras.layers',
        'tensorflow.keras.utils',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'win32serviceutil',
        'win32service',
        'win32event',
        'servicemanager',
        'schedule',
        'requests',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'base64',
        'json',
        'os',
        'sys',
        'subprocess',
        'threading',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon if available
)