@echo off
echo Starting SmartTactic Frontend with Docker...
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed.
    echo Please install Docker Desktop from https://docker.com/get-started/
    echo and make sure it's running before trying again.
    pause
    exit /b 1
)

echo Building and starting the application...
docker-compose up --build

echo.
echo Application should be available at: http://localhost:4200
echo Press Ctrl+C to stop the application
