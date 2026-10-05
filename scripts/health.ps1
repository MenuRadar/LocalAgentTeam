if (-not (Test-Path ".venv\Scripts\python.exe")) { Write-Host "Not installed. Run scripts\\install.ps1"; exit 1 }
.\.venv\Scripts\python.exe -m agent_team.main doctor
