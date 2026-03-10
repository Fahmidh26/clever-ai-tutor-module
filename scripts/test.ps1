$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

Write-Host "Running backend syntax validation..."
python -m compileall backend/app

Write-Host "Running frontend production build..."
Push-Location frontend
npm run build
Pop-Location
