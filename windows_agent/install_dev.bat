@echo off
echo Installing StressSense Windows Agent in development mode...

cd %~dp0
cd ..
pip install -e .
cd windows_agent

echo.
echo Testing if the package was installed correctly...
python -c "import windows_agent; print('Package installed successfully!')" 2>nul
if %errorLevel% neq 0 (
    echo Failed to install the package. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo You can now run the tests with: python tests.py --all
echo Or configure the agent with: python -m windows_agent --configure
pause
