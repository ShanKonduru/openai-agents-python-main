# Full-Stack Content Creation System Startup Script
Write-Host "🚀 Starting Full-Stack Content Creation System..." -ForegroundColor Green
Write-Host ""

# Check if API key is set
if (-not $env:OPENAI_API_KEY -or $env:OPENAI_API_KEY -eq "your-openai-api-key-here") {
    Write-Host "⚠️  OpenAI API key not set. Setting up..." -ForegroundColor Yellow
    & ".\006_setup_api_key.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ API key setup failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "🔑 API Key is configured" -ForegroundColor Green
Write-Host ""

# Start backend server
Write-Host "🖥️  Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python api_server.py" -WindowStyle Normal

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "📱 Starting Frontend Development Server..." -ForegroundColor Cyan
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal
Set-Location ..

Write-Host ""
Write-Host "✅ Full-Stack Application Started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
Write-Host "   • Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host "   • Backend API: http://localhost:8000" -ForegroundColor White  
Write-Host "   • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Both servers are running in separate windows." -ForegroundColor Yellow
Write-Host "   Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"