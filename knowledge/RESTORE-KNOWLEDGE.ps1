[CmdletBinding()]
param(
    [string]$CodexHome,
    [switch]$SkipIntegrityCheck,
    [switch]$ReplaceExistingJunctions
)

$ErrorActionPreference = 'Stop'
$vaultRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$markerPath = Join-Path $vaultRoot 'knowledge-base.json'

if (-not (Test-Path -LiteralPath $markerPath -PathType Leaf)) {
    throw "Not a Knowledge vault: missing $markerPath"
}

$vaultConfig = Get-Content -LiteralPath $markerPath -Raw -Encoding utf8 | ConvertFrom-Json
$activeSkillNames = @($vaultConfig.activeSkills | ForEach-Object { [string]$_ })
if ($activeSkillNames.Count -eq 0) {
    throw 'knowledge-base.json has no activeSkills.'
}

if (-not $SkipIntegrityCheck) {
    $verifyScript = Join-Path $vaultRoot '辅助\迁移\Verify-PortableManifest.ps1'
    if (Test-Path -LiteralPath $verifyScript -PathType Leaf) {
        & $verifyScript -VaultRoot $vaultRoot | Out-Host
    } else {
        Write-Warning 'Integrity script is missing; restore will continue without manifest verification.'
    }
}

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        $CodexHome = $env:CODEX_HOME
    } else {
        $CodexHome = Join-Path $env:USERPROFILE '.codex'
    }
}

$CodexHome = [System.IO.Path]::GetFullPath($CodexHome)
$skillsRoot = Join-Path $CodexHome 'skills'
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null

$skillSourceRoot = Join-Path $vaultRoot 'skill'
$registered = [System.Collections.Generic.List[object]]::new()
$conflicts = [System.Collections.Generic.List[object]]::new()

$skillDirectories = foreach ($skillName in $activeSkillNames) {
    $source = Join-Path $skillSourceRoot $skillName
    $entry = Join-Path $source 'SKILL.md'
    if (-not (Test-Path -LiteralPath $entry -PathType Leaf)) {
        throw "Active Skill is missing its entrypoint: $entry"
    }
    Get-Item -LiteralPath $source
}
$skillDirectories = @($skillDirectories | Sort-Object Name)

$unexpectedTopLevelSkills = Get-ChildItem -LiteralPath $skillSourceRoot -Directory -Force |
    Where-Object {
        (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf) -and
        ($activeSkillNames -notcontains $_.Name)
    }
if (@($unexpectedTopLevelSkills).Count -gt 0) {
    throw "Unregistered top-level SKILL.md found: $(@($unexpectedTopLevelSkills.Name) -join ', ')"
}

$nestedSkillFiles = foreach ($skillDirectory in $skillDirectories) {
    Get-ChildItem -LiteralPath $skillDirectory.FullName -Recurse -Filter 'SKILL.md' -File |
        Where-Object { $_.DirectoryName -ne $skillDirectory.FullName }
}
if (@($nestedSkillFiles).Count -gt 0) {
    $nestedRelative = @($nestedSkillFiles | ForEach-Object {
        [System.IO.Path]::GetRelativePath($vaultRoot, $_.FullName)
    })
    throw "Nested SKILL.md files would create duplicate discovery entries: $($nestedRelative -join ', ')"
}

foreach ($skillDirectory in $skillDirectories) {
    $destination = Join-Path $skillsRoot $skillDirectory.Name
    if (Test-Path -LiteralPath $destination) {
        $existing = Get-Item -LiteralPath $destination -Force
        $existingTarget = @($existing.Target) -join ';'
        $desiredTarget = [System.IO.Path]::GetFullPath($skillDirectory.FullName)
        $sameTarget = $existing.LinkType -eq 'Junction' -and
            (-not [string]::IsNullOrWhiteSpace($existingTarget)) -and
            ([System.IO.Path]::GetFullPath($existingTarget) -eq $desiredTarget)

        if ($sameTarget) {
            $registered.Add([ordered]@{ name = $skillDirectory.Name; status = 'already-registered'; target = $desiredTarget })
            continue
        }

        if ($ReplaceExistingJunctions -and $existing.LinkType -eq 'Junction') {
            Remove-Item -LiteralPath $destination -Force
        } else {
            $conflicts.Add([ordered]@{
                name           = $skillDirectory.Name
                destination    = $destination
                existingType   = [string]$existing.LinkType
                existingTarget = $existingTarget
                desiredTarget  = $desiredTarget
            })
            continue
        }
    }

    New-Item -ItemType Junction -Path $destination -Target $skillDirectory.FullName | Out-Null
    $registered.Add([ordered]@{ name = $skillDirectory.Name; status = 'registered'; target = $skillDirectory.FullName })
}

$retiredSkillFindings = [System.Collections.Generic.List[object]]::new()
foreach ($retiredName in @($vaultConfig.retiredSkillNames)) {
    $retiredPath = Join-Path $skillsRoot ([string]$retiredName)
    if (Test-Path -LiteralPath $retiredPath) {
        $item = Get-Item -LiteralPath $retiredPath -Force
        $retiredSkillFindings.Add([ordered]@{
            name     = [string]$retiredName
            path     = $retiredPath
            linkType = [string]$item.LinkType
            target   = @($item.Target) -join ';'
            action   = 'Review and disable manually; restore does not delete unrelated local Skills.'
        })
    }
}

$localConfigPath = Join-Path $vaultRoot '辅助\配置\machine-paths.local.json'
$exampleConfigPath = Join-Path $vaultRoot '辅助\配置\machine-paths.example.json'
if (-not (Test-Path -LiteralPath $localConfigPath -PathType Leaf) -and
    (Test-Path -LiteralPath $exampleConfigPath -PathType Leaf)) {
    Copy-Item -LiteralPath $exampleConfigPath -Destination $localConfigPath
}

$machinePathChecks = [ordered]@{}
if (Test-Path -LiteralPath $localConfigPath -PathType Leaf) {
    $localConfig = Get-Content -LiteralPath $localConfigPath -Raw -Encoding utf8 | ConvertFrom-Json
    foreach ($propertyName in @(
        'productionWorkRoot',
        'zhanfuBrowserRoot',
        'tiktokSkuRoot',
        'tiktokWorkspaceRoot',
        'xuanpinHome',
        'fansProjectRoot',
        'capcutDraftRoot',
        'linkfoxOutputRoot',
        'ffmpegPath',
        'videoTranscriptPython',
        'videoOcrPython',
        'whisperModelPath',
        'whisperWorkDir'
    )) {
        $configuredValue = [string]$localConfig.$propertyName
        $machinePathChecks[$propertyName] = [ordered]@{
            configured = -not [string]::IsNullOrWhiteSpace($configuredValue)
            exists     = (-not [string]::IsNullOrWhiteSpace($configuredValue)) -and (Test-Path -LiteralPath $configuredValue)
        }
    }
}

$commandChecks = [ordered]@{}
foreach ($commandName in @('ffmpeg', 'ffprobe', 'lark-cli', 'docker')) {
    $commandChecks[$commandName] = $null -ne (Get-Command $commandName -ErrorAction SilentlyContinue)
}

$environmentChecks = [ordered]@{}
foreach ($environmentName in @(
    'LINKFOXAGENT_API_KEY',
    'XUANPIN_HOME',
    'TIKTOK_SKU_ROOT',
    'FANS_PROJECT_ROOT',
    'ZHANFU_BROWSER_ROOT'
)) {
    $environmentChecks[$environmentName] = -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($environmentName))
}

$report = [ordered]@{
    restoredAt         = (Get-Date).ToUniversalTime().ToString('o')
    vaultRoot          = $vaultRoot
    codexHome          = $CodexHome
    skillsRoot         = $skillsRoot
    registeredSkills   = @($registered)
    registrationIssues = @($conflicts)
    retiredSkillsStillActive = @($retiredSkillFindings)
    localConfig        = $localConfigPath
    machinePaths       = $machinePathChecks
    commandsAvailable  = $commandChecks
    environmentPresent = $environmentChecks
    nextStep           = 'Restart Codex, then open a new conversation. Reconnect external plugins and accounts as needed.'
}

$reportPath = Join-Path $vaultRoot '辅助\日志\最近恢复报告.json'
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding utf8
$report | ConvertTo-Json -Depth 6

if ($conflicts.Count -gt 0) {
    Write-Warning 'One or more Skill registrations were skipped because an existing path was not safely replaceable.'
}


if ($retiredSkillFindings.Count -gt 0) {
    Write-Warning 'One or more retired Skill names still exist in the local Codex Skill directory. Review the restore report and disable them before relying on the seven-entry surface.'
}
