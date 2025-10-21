@echo off
REM Full-Stack Content Creation System Setup
echo 🚀 Setting up Full-Stack Content Creation System...
echo.

echo 📦 Installing Core Python Dependencies...
pip install --upgrade pip
pip install -r requirements-minimal.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install core dependencies
    timeout /t 3 /nobreak >nul
    exit /b 1
)

echo 📦 Installing FastAPI Dependencies...
pip install fastapi uvicorn python-multipart aiofiles python-dotenv markdown
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install FastAPI dependencies
    echo 💡 Trying alternative installation...
    pip install fastapi==0.100.0 uvicorn==0.23.0 python-multipart==0.0.6 aiofiles==23.2.0 python-dotenv==1.0.0 markdown==3.5.0
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to install API dependencies
        timeout /t 3 /nobreak >nul
        exit /b 1
    )
)

echo.
echo 📱 Setting up React Frontend...
cd frontend
if not exist package.json (
    echo ❌ Frontend package.json not found
    cd ..
    timeout /t 3 /nobreak >nul
    exit /b 1
)

echo Installing Node.js dependencies...
npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    cd ..
    timeout /t 3 /nobreak >nul
    exit /b 1
)

echo Building React frontend...
npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build React frontend
    cd ..
    timeout /t 3 /nobreak >nul
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
echo ✅ Setup complete! Ready to launch.
timeout /t 2 /nobreak >nul