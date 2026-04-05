param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [ValidateSet("simple", "semantic")]
    [string]$Mode = "semantic",
    [int]$Top = 5
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:UV_CACHE_DIR = Join-Path $projectRoot ".uv-cache"
New-Item -ItemType Directory -Force -Path $env:UV_CACHE_DIR | Out-Null

& "C:\Users\Admin\scoop\apps\uv\current\uv.exe" run python -m backend.scripts.query_doctype_kb `
    --query $Query `
    --mode $Mode `
    --top $Top
