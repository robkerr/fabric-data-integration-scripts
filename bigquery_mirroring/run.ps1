# Run setup_bigquery_mirror.py inside the local virtual environment.
#
# Usage:
#   .\run.ps1 [args...]
#
# Examples:
#   .\run.ps1 mirroring.yaml
#   .\run.ps1 mirroring.yaml --status
#   .\run.ps1 mirroring.yaml --stop
#   .\run.ps1 --list-connections --filter BigQuery
#   .\run.ps1 --list-mirrored-databases --workspace <WORKSPACE_ID>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
    & "$VenvDir\Scripts\pip" install --quiet -r "$ScriptDir\requirements.txt"
}

& "$VenvDir\Scripts\python" "$ScriptDir\setup_bigquery_mirror.py" @args
