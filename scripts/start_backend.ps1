param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$pydepsRoot = Join-Path $backendRoot "pydeps"

if (-not (Test-Path $pydepsRoot)) {
    throw "Missing backend dependencies at '$pydepsRoot'. Install them before starting the MVP backend."
}

$pythonPathParts = @($backendRoot, $pydepsRoot)
if ($env:PYTHONPATH) {
    $pythonPathParts += $env:PYTHONPATH
}
$env:PYTHONPATH = ($pythonPathParts -join ";")

Push-Location $backendRoot
try {
    python -m uvicorn app.main:app --host $BindHost --port $Port
}
finally {
    Pop-Location
}
