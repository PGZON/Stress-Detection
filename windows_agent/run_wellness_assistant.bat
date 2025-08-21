@echo off
echo Installing Wellness Assistant dependencies...
pip install -r requirements.txt

echo Creating icon...
python -m assets.create_icon

echo Starting Wellness Assistant...
python -m windows_agent --wellness

echo Done!
pause
