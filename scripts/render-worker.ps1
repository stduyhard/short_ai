param(
    [Parameter(Mandatory = $true)]
    [string]$JobId,

    [string]$OutputRoot = "renders"
)

if ([string]::IsNullOrWhiteSpace($JobId)) {
    throw "JobId is required."
}

$normalizedRoot = $OutputRoot.TrimEnd("/\")
$videoPath = "$normalizedRoot/$JobId/final.mp4"
$manifestPath = "$normalizedRoot/$JobId/manifest.json"

[pscustomobject]@{
    status = "queued"
    jobId = $JobId
    videoPath = $videoPath
    manifestPath = $manifestPath
    note = "render worker skeleton only; no external renderer invoked"
} | ConvertTo-Json -Depth 3
