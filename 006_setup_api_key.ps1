# OpenAI API Key Configuration for PowerShell - SECURE VERSION
# This script reads your API key from a separate file that's excluded from git

Write-Host "🔐 Setting up OpenAI API Key (Secure Method)..." -ForegroundColor Green
Write-Host ""

# Define the path for the local API key file (this file is gitignored)
$apiKeyFile = "openai_key.txt"
$apiKeyPath = Join-Path $PSScriptRoot $apiKeyFile

# Check if the API key file exists
if (-not (Test-Path $apiKeyPath)) {
    Write-Host "❌ API key file not found: $apiKeyFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "🚀 FIRST TIME SETUP:" -ForegroundColor Yellow
    Write-Host "1. Get your API key from: https://platform.openai.com/api-keys" -ForegroundColor Cyan
    Write-Host "2. Create a file named '$apiKeyFile' in this directory" -ForegroundColor Cyan
    Write-Host "3. Put ONLY your API key in that file (no quotes, no extra text)" -ForegroundColor Cyan
    Write-Host "4. The file will look like: sk-proj-..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📁 File location: $apiKeyPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔒 SECURITY: The '$apiKeyFile' file is excluded from git commits." -ForegroundColor Green
    Write-Host "   Your API key will NEVER be accidentally pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    
    # Offer to create the file interactively
    $createFile = Read-Host "Would you like to create the API key file now? (y/N)"
    if ($createFile -eq "y" -or $createFile -eq "Y") {
        Write-Host ""
        $apiKey = Read-Host "Enter your OpenAI API key" -MaskInput
        if ($apiKey -and $apiKey.StartsWith("sk-")) {
            try {
                $apiKey | Out-File -FilePath $apiKeyPath -Encoding UTF8 -NoNewline
                Write-Host "✅ API key file created successfully!" -ForegroundColor Green
                Write-Host "📁 Saved to: $apiKeyPath" -ForegroundColor Gray
            } catch {
                Write-Host "❌ Failed to create API key file: $_" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "❌ Invalid API key format. OpenAI keys start with 'sk-'" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "📝 Create the file manually and run this script again." -ForegroundColor Yellow
        exit 1
    }
}

# Read the API key from the file
try {
    $apiKey = Get-Content $apiKeyPath -Raw
    $apiKey = $apiKey.Trim()
    
    if (-not $apiKey -or -not $apiKey.StartsWith("sk-")) {
        Write-Host "❌ Invalid API key in $apiKeyFile" -ForegroundColor Red
        Write-Host "   Make sure the file contains only your API key starting with 'sk-'" -ForegroundColor Yellow
        exit 1
    }
    
    # Set the environment variable for the current session
    $env:OPENAI_API_KEY = $apiKey
    
    Write-Host "✅ OpenAI API key loaded successfully!" -ForegroundColor Green
    Write-Host "🔑 Key starts with: $($apiKey.Substring(0,7))..." -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to read API key file: $_" -ForegroundColor Red
    exit 1
}
    Write-Host "🧪 Testing the API key..." -ForegroundColor Yellow
    try {
        python -c "import openai; print('✅ OpenAI library can be imported successfully')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  OpenAI library not found. Install it with: pip install openai" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Could not test OpenAI library" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "🔄 Environment variable set for this session." -ForegroundColor Green
    Write-Host "💡 To make it permanent, add OPENAI_API_KEY to your system environment variables." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔒 SECURITY: Your API key is stored in '$apiKeyFile' (excluded from git)" -ForegroundColor Green
    Write-Host ""
    Read-Host "Press Enter to continue"
}