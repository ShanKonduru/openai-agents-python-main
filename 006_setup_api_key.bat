@echo off
REM OpenAI API Key Setup Script
REM Replace "your-openai-api-key-here" with your actual OpenAI API key

echo Setting up OpenAI API Key...
echo.

REM Set the environment variable for the current session
set OPENAI_API_KEY=your-openai-api-key-here

REM Verify it's set
if "%OPENAI_API_KEY%"=="your-openai-api-key-here" (
    echo WARNING: Please replace "your-openai-api-key-here" with your actual OpenAI API key
    echo.
    echo Instructions:
    echo 1. Edit this file: 006_setup_api_key.bat
    echo 2. Replace "your-openai-api-key-here" with your actual OpenAI API key from https://platform.openai.com/api-keys
    echo 3. Save the file
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ OpenAI API key is set successfully!
    echo Key starts with: %OPENAI_API_KEY:~0,7%...
    echo.
    echo Testing the API key...
    python -c "import openai; print('✅ OpenAI library can be imported successfully')" 2>nul
    if %ERRORLEVEL% neq 0 (
        echo ⚠️  OpenAI library not found. Install it with: pip install openai
    )
    echo.
    echo Environment variable set for this session.
    echo To make it permanent, add it to your system environment variables.
    echo.
    pause
)