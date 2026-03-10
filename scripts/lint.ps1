$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

Write-Host "Linting frontend..."
Push-Location frontend
npm run lint
Pop-Location

Write-Host "Validating backend Python syntax..."
python -m compileall backend/app
