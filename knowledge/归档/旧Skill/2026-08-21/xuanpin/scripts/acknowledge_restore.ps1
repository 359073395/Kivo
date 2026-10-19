[CmdletBinding()]
param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE '.codex')
)

$marker = Join-Path $CodexHome 'xuanpin-restore-pending.json'
if (Test-Path -LiteralPath $marker) {
    $resolvedHome = [System.IO.Path]::GetFullPath($CodexHome).TrimEnd('\')
    $resolvedMarker = [System.IO.Path]::GetFullPath($marker)
    if (-not $resolvedMarker.StartsWith($resolvedHome + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a marker outside Codex home: $resolvedMarker"
    }
    Remove-Item -LiteralPath $resolvedMarker -Force
}

