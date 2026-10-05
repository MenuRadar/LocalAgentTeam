Remove-Item -Recurse -Force .\workspaces\* -ErrorAction SilentlyContinue
New-Item -ItemType File .\workspaces\.gitkeep -Force | Out-Null
