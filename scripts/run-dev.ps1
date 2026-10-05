$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

if (-not (Test-Path $venvPython)) {
    throw "Development environment not found. Run .\scripts\setup-dev.ps1 first."
}
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    throw "Frontend dependencies not found. Run .\scripts\setup-dev.ps1 first."
}

$backendJob = Start-Job -Name "farm360-api" -ScriptBlock {
    param($python, $directory)
    Set-Location $directory
    & $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $venvPython, $backendDir

$frontendJob = Start-Job -Name "farm360-web" -ScriptBlock {
    param($directory)
    Set-Location $directory
    npm run dev -- --host 127.0.0.1
} -ArgumentList $frontendDir

Write-Host "Starting FARM360..." -ForegroundColor Cyan
Write-Host "Web: http://localhost:5173"
Write-Host "API: http://localhost:8000/api/docs"
Write-Host "Press Ctrl+C to stop both services."

try {
    while ($true) {
        Receive-Job $backendJob
        Receive-Job $frontendJob
        if ($backendJob.State -eq "Failed" -or $frontendJob.State -eq "Failed") {
            throw "A development service failed. Review the output above."
        }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
}
