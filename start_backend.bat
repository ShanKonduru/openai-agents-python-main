@echo off
REM Start Backend API Server Only
echo 🚀 Starting Content Creation API Server...
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
echo 🌐 API will be available at: http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

python api_server.py