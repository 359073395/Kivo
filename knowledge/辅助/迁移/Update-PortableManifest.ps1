[CmdletBinding()]
param(
    [string]$VaultRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
} else {
    $VaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path
}

$markerPath = Join-Path $VaultRoot 'knowledge-base.json'
if (-not (Test-Path -LiteralPath $markerPath -PathType Leaf)) {
    throw "Not a Knowledge vault: missing $markerPath"
}

$manifestPath = Join-Path $VaultRoot 'PORTABLE-MANIFEST.json'
$excludedRelativePaths = @(
    'PORTABLE-MANIFEST.json',
    '辅助\配置\machine-paths.local.json',
    '辅助\日志\最近恢复报告.json'
)
$excludedRelativePatterns = @(
    '*.pyc',
    '*\__pycache__\*'
)

function Test-IsPortableExcluded {
    param([string]$RelativePath)
    if ($excludedRelativePaths -contains $RelativePath) { return $true }
    foreach ($pattern in $excludedRelativePatterns) {
        if ($RelativePath -like $pattern) { return $true }
    }
    return $false
}

$files = Get-ChildItem -LiteralPath $VaultRoot -File -Recurse -Force |
    Where-Object {
        $relativePath = [System.IO.Path]::GetRelativePath($VaultRoot, $_.FullName)
        (-not (Test-IsPortableExcluded -RelativePath $relativePath)) -and
        ($_.Name -notlike '*.tmp')
    } |
    Sort-Object FullName |
    ForEach-Object {
        $relativePath = [System.IO.Path]::GetRelativePath($VaultRoot, $_.FullName)
        $hash = Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
        [ordered]@{
            path   = $relativePath
            bytes  = $_.Length
            sha256 = $hash.Hash.ToLowerInvariant()
        }
    }

$manifest = [ordered]@{
    schemaVersion = 1
    generatedAt   = (Get-Date).ToUniversalTime().ToString('o')
    rootMarker    = 'knowledge-base.json'
    excludes      = $excludedRelativePaths
    excludePatterns = $excludedRelativePatterns
    fileCount     = @($files).Count
    files         = @($files)
}

$temporaryManifest = "$manifestPath.tmp"
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $temporaryManifest -Encoding utf8
Move-Item -LiteralPath $temporaryManifest -Destination $manifestPath -Force

Write-Host "Portable manifest updated: $manifestPath"
Write-Host "Tracked files: $(@($files).Count)"
