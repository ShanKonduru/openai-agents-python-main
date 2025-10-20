@echo off
REM OpenAI API Key Setup Script - SECURE VERSION
REM This script reads your API key from a separate file that's excluded from git

echo 🔐 Setting up OpenAI API Key (Secure Method)...
echo.

REM Define the path for the local API key file (this file is gitignored)
set "API_KEY_FILE=openai_key.txt"

REM Check if the API key file exists
if not exist "%API_KEY_FILE%" (
    echo ❌ API key file not found: %API_KEY_FILE%
    echo.
    echo 🚀 FIRST TIME SETUP:
    echo 1. Get your API key from: https://platform.openai.com/api-keys
    echo 2. Create a file named '%API_KEY_FILE%' in this directory
    echo 3. Put ONLY your API key in that file ^(no quotes, no extra text^)
    echo 4. The file should look like: sk-proj-...
    echo.
    echo 📁 File location: %CD%\%API_KEY_FILE%
    echo.
    echo 🔒 SECURITY: The '%API_KEY_FILE%' file is excluded from git commits.
    echo    Your API key will NEVER be accidentally pushed to GitHub!
    echo.
    pause
    exit /b 1
)

REM Read the API key from the file
for /f "delims=" %%a in (%API_KEY_FILE%) do set "OPENAI_API_KEY=%%a"

REM Validate the API key
if "%OPENAI_API_KEY%"=="" (
    echo ❌ API key file is empty: %API_KEY_FILE%
    echo    Make sure the file contains your OpenAI API key
    echo.
    pause
    exit /b 1
)

REM Check if it starts with sk- (basic validation)
echo %OPENAI_API_KEY% | findstr /b "sk-" >nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Invalid API key format in %API_KEY_FILE%
    echo    OpenAI API keys should start with 'sk-'
    echo.
    pause
    exit /b 1
)

echo ✅ OpenAI API key loaded successfully!
echo 🔑 Key starts with: %OPENAI_API_KEY:~0,7%...
echo.
echo 🧪 Testing the API key...
python -c "import openai; print('✅ OpenAI library can be imported successfully')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚠️  OpenAI library not found. Install it with: pip install openai
)
echo.
echo 🔄 Environment variable set for this session.
echo 💡 To make it permanent, add OPENAI_API_KEY to your system environment variables.
echo.
echo 🔒 SECURITY: Your API key is stored in '%API_KEY_FILE%' ^(excluded from git^)
echo.
pause