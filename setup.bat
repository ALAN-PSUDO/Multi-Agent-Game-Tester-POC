@echo off
REM Setup script for Multi-Agent Game Testing System (Windows)

echo ==================================
echo Setup: Multi-Agent Game Tester
echo ==================================
echo.

echo Checking Python version...
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

echo.
echo Installing dependencies...
echo This may take a few minutes...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Failed to install dependencies
    echo Please check your internet connection and try again
    exit /b 1
)

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Quick Start:
echo   1. Test a game:
echo      python main.py --url "https://example.com/game"
echo.
echo   2. Run demo:
echo      python demo.py
echo.
echo   3. Get help:
echo      python main.py --help
echo.
echo For more information, see README.md
echo.
pause
