# Start Todo Application with Port Forwarding
# This script opens two terminals for port forwarding

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Starting Todo Application" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Step 1: Starting Backend Port Forward..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Backend Port Forward (Keep this window open)' -ForegroundColor Green; kubectl port-forward service/todo-backend 8000:8000"

Start-Sleep -Seconds 2

Write-Host "Step 2: Starting Frontend Port Forward..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Frontend Port Forward (Keep this window open)' -ForegroundColor Green; kubectl port-forward service/todo-frontend 3000:3000"

Start-Sleep -Seconds 3

Write-Host "`nStep 3: Opening application in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Application Started Successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Application URL: " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Cyan

Write-Host "`nIMPORTANT:" -ForegroundColor Red
Write-Host "  - Keep both PowerShell windows open" -ForegroundColor Yellow
Write-Host "  - DO NOT close the port-forward windows" -ForegroundColor Yellow
Write-Host "  - Press Ctrl+C in those windows to stop" -ForegroundColor Yellow

Write-Host "`nPress any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
