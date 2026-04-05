$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:UV_CACHE_DIR = Join-Path $projectRoot ".uv-cache"
New-Item -ItemType Directory -Force -Path $env:UV_CACHE_DIR | Out-Null

& "C:\Users\Admin\scoop\apps\uv\current\uv.exe" run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
 
