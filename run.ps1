# Hugging Face Chat App Launcher for PowerShell
# Run from PowerShell: .\run.ps1

Write-Host ""
Write-Host "🤖 Starting Hugging Face Chat App..." -ForegroundColor Cyan
Write-Host ""

python main.py

Write-Host ""
Write-Host "Application closed." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
