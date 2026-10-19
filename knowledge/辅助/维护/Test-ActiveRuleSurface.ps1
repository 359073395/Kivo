[CmdletBinding()]
param(
    [string]$VaultRoot,
    [switch]$FailOnWarnings
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
} else {
    $VaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path
}

$configPath = Join-Path $VaultRoot 'knowledge-base.json'
$config = Get-Content -LiteralPath $configPath -Raw -Encoding utf8 | ConvertFrom-Json
$activeNames = @($config.activeSkills | ForEach-Object { [string]$_ })
$skillRoot = Join-Path $VaultRoot 'skill'
$errors = [System.Collections.Generic.List[object]]::new()
$warnings = [System.Collections.Generic.List[object]]::new()

$topLevelSkills = Get-ChildItem -LiteralPath $skillRoot -Directory -Force |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf }
$topLevelNames = @($topLevelSkills.Name | Sort-Object)

foreach ($missing in @($activeNames | Where-Object { $topLevelNames -notcontains $_ })) {
    $errors.Add([ordered]@{ type = 'missing-active-skill'; value = $missing })
}
foreach ($unexpected in @($topLevelNames | Where-Object { $activeNames -notcontains $_ })) {
    $errors.Add([ordered]@{ type = 'unexpected-top-level-skill'; value = $unexpected })
}

foreach ($skill in $topLevelSkills) {
    $entrypointPath = Join-Path $skill.FullName 'SKILL.md'
    $entrypointText = Get-Content -LiteralPath $entrypointPath -Raw -Encoding utf8
    if (($entrypointText -notmatch 'knowledge-base\.json') -or ($entrypointText -notmatch [regex]::Escape('D:\Knowledge'))) {
        $errors.Add([ordered]@{
            type = 'missing-portable-vault-resolution-fallback'
            value = [System.IO.Path]::GetRelativePath($VaultRoot, $entrypointPath)
        })
    }
    $nested = Get-ChildItem -LiteralPath $skill.FullName -Recurse -Filter 'SKILL.md' -File |
        Where-Object { $_.DirectoryName -ne $skill.FullName }
    foreach ($item in $nested) {
        $errors.Add([ordered]@{
            type = 'nested-skill-entrypoint'
            value = [System.IO.Path]::GetRelativePath($VaultRoot, $item.FullName)
        })
    }
}

$legacyPatterns = @(
    '019f[a-f0-9-]{20,}',
    'D:\\codex项目',
    'D:\\Downloads\\zhanfu',
    'G:\\TikTokSKU',
    'F:\\zhanfu',
    'Seedance按九宫格'
)
$instructionFiles = Get-ChildItem -LiteralPath $skillRoot -Recurse -File |
    Where-Object { $_.Extension -in @('.md', '.yaml', '.yml', '.json', '.ps1', '.py') }
foreach ($file in $instructionFiles) {
    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $file.FullName) {
        $lineNumber++
        foreach ($pattern in $legacyPatterns) {
            if ($line -match $pattern) {
                $warnings.Add([ordered]@{
                    type = 'legacy-literal-in-active-surface'
                    path = [System.IO.Path]::GetRelativePath($VaultRoot, $file.FullName)
                    line = $lineNumber
                    text = $line.Trim()
                })
                break
            }
        }
    }
}

$machineConfigPath = Join-Path $VaultRoot '辅助\配置\machine-paths.local.json'
if (Test-Path -LiteralPath $machineConfigPath -PathType Leaf) {
    $machineConfig = Get-Content -LiteralPath $machineConfigPath -Raw -Encoding utf8 | ConvertFrom-Json
    foreach ($field in @(
        'productionWorkRoot',
        'zhanfuBrowserRoot',
        'tiktokSkuRoot',
        'xuanpinHome',
        'fansProjectRoot',
        'capcutDraftRoot',
        'linkfoxOutputRoot'
    )) {
        $value = [string]$machineConfig.$field
        if ([string]::IsNullOrWhiteSpace($value)) {
            $warnings.Add([ordered]@{ type = 'blank-machine-path'; field = $field })
        } elseif (-not (Test-Path -LiteralPath $value)) {
            $warnings.Add([ordered]@{ type = 'missing-machine-path'; field = $field; value = $value })
        }
    }
}

$codexHome = if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    $env:CODEX_HOME
} else {
    Join-Path $env:USERPROFILE '.codex'
}
$localSkillsRoot = Join-Path $codexHome 'skills'
foreach ($retired in @($config.retiredSkillNames)) {
    $candidate = Join-Path $localSkillsRoot ([string]$retired)
    if (Test-Path -LiteralPath $candidate) {
        $warnings.Add([ordered]@{
            type = 'retired-skill-still-installed'
            name = [string]$retired
            path = $candidate
        })
    }
}

$result = [ordered]@{
    vaultRoot = $VaultRoot
    checkedAt = (Get-Date).ToUniversalTime().ToString('o')
    expectedActiveSkills = @($activeNames)
    discoveredTopLevelSkills = @($topLevelNames)
    activeSkillCount = $topLevelNames.Count
    errors = @($errors)
    warnings = @($warnings)
    passed = ($errors.Count -eq 0)
}

$result | ConvertTo-Json -Depth 6

if ($errors.Count -gt 0) {
    throw 'Active rule surface validation failed.'
}
if ($FailOnWarnings -and $warnings.Count -gt 0) {
    throw 'Active rule surface contains warnings.'
}
