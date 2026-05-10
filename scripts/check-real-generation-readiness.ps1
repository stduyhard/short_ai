param(
    [string]$BackendUrl = "http://127.0.0.1:8000"
)

$readiness = [ordered]@{
    OpenAIKeyConfigured = [bool]$env:OPENAI_API_KEY
    DashScopeKeyConfigured = [bool]$env:DASHSCOPE_API_KEY
    FfmpegOnPath = [bool](Get-Command ffmpeg -ErrorAction SilentlyContinue)
    BackendReachable = $false
    BackendReportedReady = $false
}

try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/api/runtime/readiness" -Method Get -TimeoutSec 5
    $readiness.BackendReachable = $true
    $readiness.BackendReportedReady = [bool]$response.readyForRealGeneration
    $readiness.BackendProvidersConfigured = [bool]$response.providersConfigured
    $readiness.BackendFfmpegAvailable = [bool]$response.ffmpegAvailable
}
catch {
    $readiness.BackendError = $_.Exception.Message
}

$readiness

if (-not $readiness.OpenAIKeyConfigured -and -not $readiness.DashScopeKeyConfigured) {
    Write-Warning "Neither OPENAI_API_KEY nor DASHSCOPE_API_KEY is configured."
}

if (-not $readiness.FfmpegOnPath) {
    Write-Warning "ffmpeg is not available on PATH. Install ffmpeg or set FFMPEG_BINARY."
}

if (-not $readiness.BackendReachable) {
    Write-Warning "Backend is not reachable at /api/runtime/readiness."
}
