$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

Write-Host "Starting full local stack with docker compose..."
docker compose up --build
