$ErrorActionPreference='Stop'
Start-Process powershell -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-File","$PSScriptRoot\start.ps1"
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8787"
