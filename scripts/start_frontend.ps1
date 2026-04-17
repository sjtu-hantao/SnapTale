param(
    [switch]$NoBrowser
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"
$fallbackNodeRoot = "C:\Users\user\Documents\New project\dso_slides_work\tools\node-v20.19.2-win-x64"

$npmCommand = $null
if (Get-Command npm.cmd -ErrorAction SilentlyContinue) {
    $npmCommand = "npm.cmd"
}
elseif (Test-Path (Join-Path $fallbackNodeRoot "npm.cmd")) {
    $env:Path = "$fallbackNodeRoot;$env:Path"
    $npmCommand = Join-Path $fallbackNodeRoot "npm.cmd"
}
else {
    throw "Couldn't find npm.cmd. Add Node.js to PATH or update the fallback path in scripts/start_frontend.ps1."
}

if ($NoBrowser) {
    $env:BROWSER = "none"
}

Push-Location $frontendRoot
try {
    & $npmCommand start
}
finally {
    Pop-Location
}
