@echo off
cd %~dp0
echo Installing required packages from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% == 0 (
    echo Requirements installed successfully.
) else (
    echo Failed to install requirements. Check the error messages above for details.
)
pause
