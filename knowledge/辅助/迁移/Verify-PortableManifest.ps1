[CmdletBinding()]
param(
    [string]$VaultRoot,
    [switch]$FailOnUntracked
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
} else {
    $VaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path
}

$manifestPath = Join-Path $VaultRoot 'PORTABLE-MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Portable manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$excludedRelativePaths = @($manifest.excludes)
$excludedRelativePatterns = @('*.pyc', '*\__pycache__\*')
if ($null -ne $manifest.PSObject.Properties['excludePatterns']) {
    $excludedRelativePatterns = @($excludedRelativePatterns + @($manifest.excludePatterns) | Sort-Object -Unique)
}

function Test-IsPortableExcluded {
    param([string]$RelativePath)
    if ($excludedRelativePaths -contains $RelativePath) { return $true }
    foreach ($pattern in $excludedRelativePatterns) {
        if ($RelativePath -like $pattern) { return $true }
    }
    return $false
}

$expectedByPath = @{}
foreach ($entry in @($manifest.files)) {
    $expectedByPath[[string]$entry.path] = $entry
}

$missing = [System.Collections.Generic.List[string]]::new()
$mismatched = [System.Collections.Generic.List[object]]::new()

foreach ($relativePath in ($expectedByPath.Keys | Sort-Object)) {
    $entry = $expectedByPath[$relativePath]
    $fullPath = Join-Path $VaultRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        $missing.Add($relativePath)
        continue
    }

    $item = Get-Item -LiteralPath $fullPath
    $actualHash = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if (($item.Length -ne [long]$entry.bytes) -or ($actualHash -ne [string]$entry.sha256)) {
        $mismatched.Add([ordered]@{
            path           = $relativePath
            expectedBytes  = [long]$entry.bytes
            actualBytes    = $item.Length
            expectedSha256 = [string]$entry.sha256
            actualSha256   = $actualHash
        })
    }
}

$untracked = Get-ChildItem -LiteralPath $VaultRoot -File -Recurse -Force |
    ForEach-Object { [System.IO.Path]::GetRelativePath($VaultRoot, $_.FullName) } |
    Where-Object {
        ($_ -ne 'PORTABLE-MANIFEST.json') -and
        (-not (Test-IsPortableExcluded -RelativePath $_)) -and
        ($_ -notlike '*.tmp') -and
        (-not $expectedByPath.ContainsKey($_))
    } |
    Sort-Object

$result = [ordered]@{
    vaultRoot       = $VaultRoot
    generatedAt     = [string]$manifest.generatedAt
    trackedFiles    = @($manifest.files).Count
    missing         = @($missing)
    mismatched      = @($mismatched)
    untracked       = @($untracked)
    integrityPassed = ($missing.Count -eq 0 -and $mismatched.Count -eq 0)
}

$result | ConvertTo-Json -Depth 6

if (-not $result.integrityPassed) {
    throw "Knowledge vault integrity verification failed."
}

if ($FailOnUntracked -and @($untracked).Count -gt 0) {
    throw "Knowledge vault contains untracked files. Update the manifest after reviewing them."
}
