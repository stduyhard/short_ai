param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$frontendRoot = Join-Path $repoRoot "frontend"

if (-not (Test-Path $backendRoot)) {
    throw "Backend directory not found: $backendRoot"
}

if (-not (Test-Path $frontendRoot)) {
    throw "Frontend directory not found: $frontendRoot"
}

$backendCommand = "Set-Location '$backendRoot'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
$frontendCommand = "Set-Location '$frontendRoot'; `$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:$BackendPort'; npm run dev -- --hostname 127.0.0.1 --port $FrontendPort"

$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $backendCommand -PassThru

try {
    Write-Host "Backend started in a new PowerShell window: http://127.0.0.1:$BackendPort"
    Write-Host "Starting frontend in the current window: http://127.0.0.1:$FrontendPort"
    Invoke-Expression $frontendCommand
}
finally {
    if ($null -ne $backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id
    }
}
