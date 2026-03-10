.PHONY: dev test migrate seed lint format

dev:
	powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

test:
	powershell -ExecutionPolicy Bypass -File scripts/test.ps1

migrate:
	powershell -ExecutionPolicy Bypass -File scripts/migrate.ps1

seed:
	powershell -ExecutionPolicy Bypass -File scripts/seed.ps1

lint:
	powershell -ExecutionPolicy Bypass -File scripts/lint.ps1

format:
	powershell -ExecutionPolicy Bypass -File scripts/format.ps1
