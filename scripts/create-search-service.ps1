param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $true)]
    [string]$ServiceName,

    [string]$Location = "southeastasia",
    [ValidateSet("free", "basic", "standard")]
    [string]$Sku = "basic",
    [ValidateSet("free", "standard", "disabled")]
    [string]$SemanticSearch = "free"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:AZURE_CONFIG_DIR = Join-Path $projectRoot ".azure"
New-Item -ItemType Directory -Force -Path $env:AZURE_CONFIG_DIR | Out-Null

& "C:\Users\Admin\scoop\shims\az.cmd" group create `
    --name $ResourceGroup `
    --location $Location `
    --output table

& "C:\Users\Admin\scoop\shims\az.cmd" search service create `
    --resource-group $ResourceGroup `
    --name $ServiceName `
    --location $Location `
    --sku $Sku `
    --partition-count 1 `
    --replica-count 1 `
    --semantic-search $SemanticSearch `
    --auth-options aadOrApiKey `
    --output table

Write-Host ""
Write-Host "Search endpoint:"
Write-Host "https://$ServiceName.search.windows.net"
