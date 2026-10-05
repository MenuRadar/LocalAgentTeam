$ErrorActionPreference='Stop'
Write-Host "=== LocalAgentTeam Windows Installer ===" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.11+ is required. Install it from https://www.python.org/downloads/windows/ and enable PATH." }
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[all]"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
Write-Host ""
Write-Host "Installation complete." -ForegroundColor Green
Write-Host "1) Edit .env and add your provider keys."
Write-Host "2) Run .\scripts\start.ps1"
Write-Host "3) Open http://127.0.0.1:8787"
