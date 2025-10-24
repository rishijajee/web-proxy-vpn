@echo off
REM Quick Start Script for Google Docs Proxy VPN (Windows)
REM This script automates the setup process

echo ======================================================================
echo   Google Docs Proxy VPN - Quick Start
echo ======================================================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Check Chrome installation
echo.
echo Checking Chrome installation...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Found Google Chrome
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo Found Google Chrome
) else (
    echo Chrome not found. Some features may not work.
    echo Download from: https://www.google.com/chrome/
)

REM Create virtual environment
echo.
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo All dependencies installed successfully!

REM Check for client_secrets.json
echo.
echo Checking for Google OAuth credentials...
if not exist "client_secrets.json" (
    echo client_secrets.json not found!
    echo.
    echo To set up Google OAuth:
    echo    1. Go to https://console.cloud.google.com
    echo    2. Create a new project
    echo    3. Enable Google Drive API and Google Docs API
    echo    4. Create OAuth 2.0 credentials ^(Web application^)
    echo    5. Add redirect URI: http://localhost:5000/oauth2callback
    echo    6. Download client_secrets.json and place it in this directory
    echo.
    echo    See SETUP_GUIDE.md for detailed instructions.
) else (
    echo client_secrets.json found
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "downloads" mkdir downloads
if not exist ".config" mkdir .config
echo Directories created

REM Test network connectivity
echo.
echo Testing network connectivity...
python -c "from network_checker import NetworkChecker; checker = NetworkChecker(); status = checker.get_network_status(); print(f'Network Status: {status[\"status\"]}'); print(f'Message: {status[\"message\"]}')"

REM Summary
echo.
echo ======================================================================
echo   Setup Complete!
echo ======================================================================
echo.
echo To start the application:
echo    1. Activate virtual environment: venv\Scripts\activate.bat
echo    2. Run the app: python app_google.py
echo    3. Open browser: http://localhost:5000
echo.
echo For detailed instructions, see:
echo    - SETUP_GUIDE.md (Complete setup guide)
echo    - README_GOOGLE_DOCS.md (Feature documentation)
echo.
echo Next steps:
if not exist "client_secrets.json" (
    echo    - Set up Google OAuth (see instructions above)
)
echo    - Configure proxy if needed (Settings page)
echo    - Login with Google account
echo    - Start browsing and managing files!
echo.
echo ======================================================================

pause
