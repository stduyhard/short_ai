param(
    [string]$BackendUrl = "http://127.0.0.1:8000",
    [string]$Topic = "AI 短视频工具推荐",
    [string]$Style = "干货",
    [string]$Voice = "auto",
    [int]$PollIntervalSeconds = 3,
    [int]$MaxPollCount = 20
)

$readiness = Invoke-RestMethod -Uri "$BackendUrl/api/runtime/readiness" -Method Get -TimeoutSec 10

if (-not $readiness.readyForRealGeneration) {
    throw "Backend is not ready for real generation. Check /api/runtime/readiness first."
}

$createPayload = @{
    topic = $Topic
    style = $Style
    voice = $Voice
} | ConvertTo-Json

$job = Invoke-RestMethod -Uri "$BackendUrl/api/jobs" -Method Post -ContentType "application/json" -Body $createPayload
$jobId = $job.job_id

if (-not $jobId) {
    throw "Failed to create job."
}

[void](Invoke-RestMethod -Uri "$BackendUrl/api/jobs/$jobId/run" -Method Post -TimeoutSec 30)

$detail = $null
for ($attempt = 0; $attempt -lt $MaxPollCount; $attempt++) {
    Start-Sleep -Seconds $PollIntervalSeconds
    $detail = Invoke-RestMethod -Uri "$BackendUrl/api/jobs/$jobId" -Method Get -TimeoutSec 30

    if ($detail.status -in @("completed", "degraded", "failed")) {
        break
    }
}

if ($null -eq $detail) {
    throw "Failed to retrieve job detail."
}

$result = [ordered]@{
    jobId = $detail.jobId
    status = $detail.status
    voiceSelection = $detail.voiceSelection
    voiceAsset = $detail.voiceAsset
    finalVideo = $detail.finalVideo
    errorMessage = $detail.errorMessage
}

$result
