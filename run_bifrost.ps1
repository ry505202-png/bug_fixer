# PowerShell Script to Launch Bifrost Gateway with Configured Providers & Governance
param(
    [string]$AppDir = "./bifrost"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting Maxim AI Bifrost LLM Gateway                  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Load .env file if present
$EnvFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $EnvFile) {
    Write-Host "[Info] Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $varName = $parts[0].Trim()
            $varVal = $parts[1].Trim()
            if (-not [System.Environment]::GetEnvironmentVariable($varName)) {
                [System.Environment]::SetEnvironmentVariable($varName, $varVal, "Process")
            }
        }
    }
}

# Ensure minimum required defaults
if (-not $env:BIFROST_ENCRYPTION_KEY) {
    $env:BIFROST_ENCRYPTION_KEY = "0123456789abcdef0123456789abcdef"
}
if (-not $env:BIFROST_VIRTUAL_KEY) {
    $env:BIFROST_VIRTUAL_KEY = "sk-bf-nano-agent-secret-key"
}

Write-Host "[Config] App Directory : $AppDir" -ForegroundColor Cyan
Write-Host "[Config] Virtual Key   : $env:BIFROST_VIRTUAL_KEY" -ForegroundColor Cyan
Write-Host "[Info] Executing npx -y @maximhq/bifrost -app-dir $AppDir..." -ForegroundColor Green
Write-Host "[Note] Web UI will be accessible at http://localhost:8080" -ForegroundColor Gray

npx -y @maximhq/bifrost -app-dir $AppDir

