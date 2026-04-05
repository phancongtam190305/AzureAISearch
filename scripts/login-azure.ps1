$ErrorActionPreference = "Stop"

$env:AZURE_CONFIG_DIR = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path ".azure"
New-Item -ItemType Directory -Force -Path $env:AZURE_CONFIG_DIR | Out-Null

& "C:\Users\Admin\scoop\shims\az.cmd" login --use-device-code
