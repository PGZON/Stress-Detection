"""
PyInstaller spec file for StressSense Wellness Assistant
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Ensure we have the icon first
from windows_agent.assets.create_icon import create_icon
icon_path = create_icon()

# Define base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Add data files
datas = [
    (os.path.join(base_dir, 'assets'), 'assets')
]

# Deep Face models
datas += collect_data_files('deepface')

a = Analysis(
    [os.path.join(base_dir, '__main__.py')],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=['PyQt5.sip'],
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
    [],
    exclude_binaries=True,
    name='StressSense_Wellness',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StressSense_Wellness',
)

# For single file build
exe_single = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StressSense_Wellness_Single',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
