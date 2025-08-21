@echo off
echo Building StressSense Wellness Assistant executable...
pip install -r requirements.txt
python -m PyInstaller wellness.spec --noconfirm

echo Build complete!
echo Executable is in dist\StressSense_Wellness folder
echo Single file executable is at dist\StressSense_Wellness_Single.exe
pause
