param(
    [int]$BackendPort = 8001,
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

function Stop-ListeningProcessByPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $connections = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    if ($connections.Count -eq 0) {
        Write-Host "Port $Port is available."
        return
    }

    $processIds = $connections |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ -and $_ -gt 0 }

    foreach ($processId in $processIds) {
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "Closed process $processId using port $Port."
        }
        catch {
            throw "Failed to stop process $processId on port $Port. $($_.Exception.Message)"
        }
    }

    Start-Sleep -Seconds 1
}

Stop-ListeningProcessByPort -Port $BackendPort
Stop-ListeningProcessByPort -Port $FrontendPort

$backendCommand = "Set-Location '$backendRoot'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
$frontendCommand = "Set-Location '$frontendRoot'; `$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:$BackendPort'; npm run dev -- --hostname 127.0.0.1 --port $FrontendPort"

$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $backendCommand -PassThru
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $frontendCommand -PassThru

if ($null -eq $backendProcess -or $backendProcess.HasExited) {
    throw "Backend window failed to start."
}

if ($null -eq $frontendProcess -or $frontendProcess.HasExited) {
    throw "Frontend window failed to start."
}

Write-Host "Backend started in a new PowerShell window: http://127.0.0.1:$BackendPort"
Write-Host "Frontend started in a new PowerShell window: http://127.0.0.1:$FrontendPort"
