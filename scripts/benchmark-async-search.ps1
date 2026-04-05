param(
    [string]$Query = "Azure AI Search",
    [ValidateSet("simple", "semantic")]
    [string]$Mode = "semantic",
    [int]$Top = 5,
    [int]$Concurrency = 5,
    [int]$Requests = 20
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:UV_CACHE_DIR = Join-Path $projectRoot ".uv-cache"
New-Item -ItemType Directory -Force -Path $env:UV_CACHE_DIR | Out-Null

& "C:\Users\Admin\scoop\apps\uv\current\uv.exe" run python -m backend.scripts.benchmark_async_search `
    --query $Query `
    --mode $Mode `
    --top $Top `
    --concurrency $Concurrency `
    --requests $Requests
