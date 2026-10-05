$ErrorActionPreference='Stop'
if (-not (Test-Path ".venv\Scripts\python.exe")) { Write-Host "Run scripts\\install.ps1 first." -ForegroundColor Yellow; exit 1 }
if (Test-Path ".env") { Get-Content ".env" | Where-Object { $_ -and -not $_.StartsWith("#") } | ForEach-Object { $p=$_.Split("=",2); if($p.Count -eq 2){ [Environment]::SetEnvironmentVariable($p[0],$p[1],"Process") } } }
.\.venv\Scripts\python.exe -m agent_team.main doctor
Write-Host "Starting LocalAgentTeam at http://127.0.0.1:8787" -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m agent_team.main web --host 127.0.0.1 --port 8787
