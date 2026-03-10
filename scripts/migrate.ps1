$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

Write-Host "Applying schema migration (init.sql) to tutor-db..."
docker compose exec -T tutor-db psql -U postgres -d clever_ai_tutor -f /docker-entrypoint-initdb.d/01-init.sql
