@echo off
REM Start Full-Stack Content Creation System
echo 🚀 Starting Full-Stack Content Creation System...
echo.

REM Check if API key is set
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  OpenAI API key not set. Setting up...
    call 006_setup_api_key.bat
    if %ERRORLEVEL% neq 0 (
        echo ❌ API key setup failed
        timeout /t 3 /nobreak >nul
        exit /b 1
    )
)

echo 🔑 API Key is configured
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🐍 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo 🖥️  Starting Backend Server...
start "Content Creation API" cmd /k "call .venv\Scripts\activate.bat && python real_api_server.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 📱 Starting Frontend Development Server...
cd frontend
start "React Frontend" cmd /k "npm start"

cd ..

echo.
echo ✅ Full-Stack Application Started!
echo.
echo 🌐 Application URLs:
echo    • Frontend UI: http://localhost:3000
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo.
echo 💡 Both servers are running in separate windows.
echo    Close those windows to stop the servers.
echo.
echo ⚡ Startup complete! Check the opened windows for server status.