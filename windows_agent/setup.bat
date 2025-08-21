@echo off
echo StressSense Windows Agent Setup
echo ==============================

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This setup requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo Installing the package in development mode...
cd ..
pip install -e .
cd windows_agent

echo.
echo Installing Python requirements...
pip install -r requirements.txt

echo.
echo Setting up agent...
python -m windows_agent --configure

echo.
echo Would you like to register this device now? [Y/N]
set /p register=

if /i "%register%"=="Y" (
    echo.
    echo Please enter your employee ID:
    set /p employee_id=
    
    echo.
    echo Registering device...
    python -m windows_agent --register %employee_id%
)

echo.
echo Setup complete!
echo You can now run the agent with: python -m windows_agent

echo.
echo Would you like to install as a Windows service? [Y/N]
set /p service=

if /i "%service%"=="Y" (
    echo Installing as a Windows service...
    python -m windows_agent.service install
    echo Service installed successfully.
    
    echo Would you like to start the service now? [Y/N]
    set /p start_service=
    
    if /i "%start_service%"=="Y" (
        echo Starting service...
        python -m windows_agent.service start
        echo Service started.
    ) else (
        echo You can start the service later with: python -m windows_agent.service start
    )
)

echo.
echo Thank you for installing StressSense Windows Agent!
pause
