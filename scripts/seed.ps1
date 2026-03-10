$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

Write-Host "Applying seed data (seed.sql) to tutor-db..."
docker compose exec -T tutor-db psql -U postgres -d clever_ai_tutor -f /docker-entrypoint-initdb.d/02-seed.sql
