# OpenAI API Key Configuration for PowerShell
# Replace "your-openai-api-key-here" with your actual OpenAI API key

Write-Host "Setting up OpenAI API Key..." -ForegroundColor Green
Write-Host ""

# Set the environment variable for the current session
$env:OPENAI_API_KEY = "your-openai-api-key-here"

# Verify it's set
if ($env:OPENAI_API_KEY -eq "your-openai-api-key-here") {
    Write-Host "WARNING: Please replace 'your-openai-api-key-here' with your actual OpenAI API key" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Yellow
    Write-Host "1. Edit this file: 006_setup_api_key.ps1"
    Write-Host "2. Replace 'your-openai-api-key-here' with your actual OpenAI API key from https://platform.openai.com/api-keys"
    Write-Host "3. Save the file"
    Write-Host "4. Run this script again"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host "✅ OpenAI API key is set successfully!" -ForegroundColor Green
    Write-Host "Key starts with: $($env:OPENAI_API_KEY.Substring(0,7))..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Testing the API key..." -ForegroundColor Yellow
    try {
        python -c "import openai; print('✅ OpenAI library can be imported successfully')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  OpenAI library not found. Install it with: pip install openai" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Could not test OpenAI library" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Environment variable set for this session." -ForegroundColor Green
    Write-Host "To make it permanent, add it to your system environment variables." -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue"
}