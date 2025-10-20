@echo off
REM Full-Stack Content Creation System Setup
echo 🚀 Setting up Full-Stack Content Creation System...
echo.

echo 📦 Installing Python Backend Dependencies...
pip install -r requirements-api.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo 📱 Setting up React Frontend...
cd frontend
if not exist package.json (
    echo ❌ Frontend package.json not found
    cd ..
    pause
    exit /b 1
)

echo Installing Node.js dependencies...
npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)

echo Building React frontend...
npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build React frontend
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ✅ Setup completed successfully!
echo.
echo 🎯 To start the application:
echo    1. Run backend:  python api_server.py
echo    2. Run frontend: cd frontend && npm start
echo.
echo 🌐 Application URLs:
echo    • Frontend: http://localhost:3000
echo    • Backend API: http://localhost:8000
echo    • API Docs: http://localhost:8000/docs
echo.
pause