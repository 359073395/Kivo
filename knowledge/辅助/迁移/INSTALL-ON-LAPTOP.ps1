[CmdletBinding()]
param(
    [string]$BaseDirectory,
    [string]$CodexHome,
    [switch]$SkipBusinessFiles,
    [switch]$SkipCodexRegistration,
    [switch]$SkipUserEnvironmentVariables,
    [switch]$VerifyOnly,
    [switch]$PlanOnly
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

if ($PSVersionTable.PSVersion.Major -lt 7) {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($null -eq $pwsh) {
        throw '需要 PowerShell 7。请先安装 PowerShell 7，然后重新运行同一条命令。'
    }
    & $pwsh.Source -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath
    exit $LASTEXITCODE
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$kitRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$kitConfigPath = Join-Path $kitRoot 'MIGRATION-KIT.json'
if (-not (Test-Path -LiteralPath $kitConfigPath -PathType Leaf)) {
    throw "迁移套件缺少 MIGRATION-KIT.json：$kitConfigPath"
}
$kit = Get-Content -LiteralPath $kitConfigPath -Raw -Encoding utf8 | ConvertFrom-Json

function Get-Sha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Resolve-KitFile($Record) {
    $name = [string]$Record.name
    if ([string]::IsNullOrWhiteSpace($name) -or [System.IO.Path]::IsPathRooted($name) -or $name.Contains('..')) {
        throw "套件文件名不安全：$name"
    }
    $path = [System.IO.Path]::GetFullPath((Join-Path $kitRoot $name))
    if (-not $path.StartsWith($kitRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "套件文件越出目录：$name"
    }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "套件文件缺失：$path" }
    $item = Get-Item -LiteralPath $path
    if ($item.Length -ne [int64]$Record.bytes) { throw "套件文件大小不符：$name" }
    if ((Get-Sha256 $path) -ne ([string]$Record.sha256).ToLowerInvariant()) { throw "套件文件 SHA-256 不符：$name" }
    $path
}

function Test-ManifestArchive([string]$ZipPath, [string]$ManifestEntryName) {
    $stream = [System.IO.File]::OpenRead($ZipPath)
    try {
        $archive = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Read, $true)
        try {
            $entries = @($archive.Entries)
            $duplicates = @($entries | Group-Object FullName | Where-Object Count -gt 1)
            if ($duplicates.Count -gt 0) { throw "ZIP 含重复条目：$($duplicates.Name -join ', ')" }
            $entryMap = @{}
            foreach ($entry in $entries) { $entryMap[$entry.FullName] = $entry }
            if (-not $entryMap.ContainsKey($ManifestEntryName)) { throw "ZIP 缺少内部清单：$ManifestEntryName" }
            $reader = [System.IO.StreamReader]::new($entryMap[$ManifestEntryName].Open(), [System.Text.Encoding]::UTF8)
            try { $manifest = $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
            foreach ($record in @($manifest.files)) {
                $name = ([string]$record.path).Replace('\', '/')
                if (-not $entryMap.ContainsKey($name)) { throw "ZIP 缺少清单文件：$name" }
                $entry = $entryMap[$name]
                if ($entry.Length -ne [int64]$record.bytes) { throw "ZIP 条目大小不符：$name" }
                $sha = [System.Security.Cryptography.SHA256]::Create()
                try {
                    $entryStream = $entry.Open()
                    try { $actual = ([System.BitConverter]::ToString($sha.ComputeHash($entryStream))).Replace('-', '').ToLowerInvariant() }
                    finally { $entryStream.Dispose() }
                } finally { $sha.Dispose() }
                if ($actual -ne ([string]$record.sha256).ToLowerInvariant()) { throw "ZIP 条目 SHA-256 不符：$name" }
            }
            [ordered]@{ path = $ZipPath; entries = $entries.Count; trackedFiles = @($manifest.files).Count; passed = $true }
        } finally { $archive.Dispose() }
    } finally { $stream.Dispose() }
}

function Assert-EmptyTarget([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        if (@(Get-ChildItem -LiteralPath $Path -Force).Count -gt 0) {
            throw "目标目录已存在且非空，为防覆盖已停止：$Path"
        }
    }
}

function Expand-ArchiveSafe([string]$ZipPath, [string]$Destination) {
    if (Test-Path -LiteralPath $Destination) { throw "临时目录已存在：$Destination" }
    New-Item -ItemType Directory -Path $Destination | Out-Null
    [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $Destination)
}

$coreZip = Resolve-KitFile $kit.files.core
$businessZip = if (-not $SkipBusinessFiles) { Resolve-KitFile $kit.files.businessFiles } else { $null }
$installerFile = Resolve-KitFile $kit.files.installer
$guideFile = Resolve-KitFile $kit.files.guide
$verification = [System.Collections.Generic.List[object]]::new()
$verification.Add((Test-ManifestArchive $coreZip 'PORTABLE-MANIFEST.json'))
if ($null -ne $businessZip) { $verification.Add((Test-ManifestArchive $businessZip 'PAYLOAD-MANIFEST.json')) }

if ([string]::IsNullOrWhiteSpace($BaseDirectory)) { $BaseDirectory = 'G:\' }
$base = [System.IO.Path]::GetFullPath($BaseDirectory)
$effectiveCodexHome = if (-not [string]::IsNullOrWhiteSpace($CodexHome)) {
    [System.IO.Path]::GetFullPath($CodexHome)
} elseif (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    [System.IO.Path]::GetFullPath($env:CODEX_HOME)
} else {
    Join-Path $env:USERPROFILE '.codex'
}
$driveRootInstall = $base -match '^[A-Za-z]:\\$'
$vaultRoot = [System.IO.Path]::Combine($base, 'Knowledge')
$workRoot = if ($driveRootInstall) { [System.IO.Path]::Combine($base, '820') } else { [System.IO.Path]::Combine($base, 'KnowledgeWork') }
$skuRoot = if ($driveRootInstall) { [System.IO.Path]::Combine($base, 'codex', 'TikTokSKU') } else { [System.IO.Path]::Combine($base, 'TikTokSKU') }
$tiktokWorkspace = if ($driveRootInstall) { [System.IO.Path]::Combine($base, 'codex', 'TikTok') } else { [System.IO.Path]::Combine($base, 'TikTokWorkspace') }

$plan = [ordered]@{
    kitRoot = $kitRoot
    generatedAt = [string]$kit.generatedAt
    baseDirectory = $base
    vaultRoot = $vaultRoot
    productionWorkRoot = if ($SkipBusinessFiles) { $null } else { $workRoot }
    tiktokSkuRoot = if ($SkipBusinessFiles) { $null } else { $skuRoot }
    tiktokWorkspaceRoot = if ($SkipBusinessFiles) { $null } else { $tiktokWorkspace }
    verifiedArchives = @($verification)
    verifiedInstaller = $installerFile
    verifiedGuide = $guideFile
    willRegisterCodexSkills = -not $SkipCodexRegistration
    codexHome = $effectiveCodexHome
    willSetUserEnvironmentVariables = -not $SkipUserEnvironmentVariables
    environmentsAndLoginsMustBeReinstalled = $true
}
if ($VerifyOnly -or $PlanOnly) {
    $plan | ConvertTo-Json -Depth 7
    exit 0
}

Assert-EmptyTarget $vaultRoot
if (-not $SkipBusinessFiles) {
    Assert-EmptyTarget $workRoot
    Assert-EmptyTarget $skuRoot
    Assert-EmptyTarget $tiktokWorkspace
}
if ($driveRootInstall -and -not (Test-Path -LiteralPath $base -PathType Container)) {
    throw "固定安装盘不存在：$base。请先确认笔记本 G: 盘可用。"
}
New-Item -ItemType Directory -Path $base -Force | Out-Null
$stageRoot = Join-Path $base ('.knowledge-install-' + [guid]::NewGuid().ToString('N'))
if (-not $stageRoot.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) { throw '临时目录越出安装根目录。' }
try {
    $coreStage = Join-Path $stageRoot 'core'
    Expand-ArchiveSafe $coreZip $coreStage
    Move-Item -LiteralPath $coreStage -Destination $vaultRoot

    if (-not $SkipBusinessFiles) {
        $businessStage = Join-Path $stageRoot 'business'
        Expand-ArchiveSafe $businessZip $businessStage
        New-Item -ItemType Directory -Path (Split-Path $skuRoot -Parent) -Force | Out-Null
        New-Item -ItemType Directory -Path (Split-Path $tiktokWorkspace -Parent) -Force | Out-Null
        Move-Item -LiteralPath (Join-Path $businessStage 'TikTokSKU') -Destination $skuRoot
        Move-Item -LiteralPath (Join-Path $businessStage 'ProductionWork') -Destination $workRoot
        Move-Item -LiteralPath (Join-Path $businessStage 'TikTokWorkspace') -Destination $tiktokWorkspace
    } else {
        New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    }
    New-Item -ItemType Directory -Path (Join-Path $workRoot 'rule-effects\pending') -Force | Out-Null

    $xuanpinHome = Join-Path $tiktokWorkspace '选品对标爆款Skill\select-benchmark-rewrite-tiktok'
    $machineConfig = [ordered]@{
        schemaVersion = 1
        productionWorkRoot = $workRoot
        zhanfuBrowserRoot = ''
        tiktokSkuRoot = if ($SkipBusinessFiles) { '' } else { $skuRoot }
        tiktokWorkspaceRoot = if ($SkipBusinessFiles) { '' } else { $tiktokWorkspace }
        xuanpinHome = if (-not $SkipBusinessFiles -and (Test-Path -LiteralPath $xuanpinHome -PathType Container)) { $xuanpinHome } else { '' }
        fansProjectRoot = ''
        capcutDraftRoot = ''
        linkfoxOutputRoot = ''
        ffmpegPath = ''
        videoTranscriptPython = ''
        videoOcrPython = ''
        whisperModelPath = ''
        whisperWorkDir = Join-Path $workRoot 'whisper'
        updatedAt = (Get-Date).ToString('o')
        notes = @(
            'Laptop file migration completed; software environments must be reinstalled.',
            'API keys, OAuth tokens, cookies and passwords were intentionally excluded.'
        )
    }
    $machineConfigPath = Join-Path $vaultRoot '辅助\配置\machine-paths.local.json'
    $machineConfig | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $machineConfigPath -Encoding utf8
    if (-not $SkipUserEnvironmentVariables) {
        [Environment]::SetEnvironmentVariable('KNOWLEDGE_BASE_ROOT', $vaultRoot, 'User')
        [Environment]::SetEnvironmentVariable('PRODUCTION_WORK_ROOT', $workRoot, 'User')
        if (-not $SkipBusinessFiles) { [Environment]::SetEnvironmentVariable('TIKTOK_SKU_ROOT', $skuRoot, 'User') }
    }

    if (-not $SkipCodexRegistration) {
        $restore = Join-Path $vaultRoot 'RESTORE-KNOWLEDGE.ps1'
        & $restore -CodexHome $effectiveCodexHome -ReplaceExistingJunctions | Out-Host
        if (-not $?) { throw '七个主 Skill 注册失败。' }
    }

    & (Join-Path $vaultRoot '辅助\迁移\Verify-PortableManifest.ps1') -VaultRoot $vaultRoot -FailOnUntracked | Out-Host
    if (-not $?) { throw '知识库清单严格验证失败。' }
    & (Join-Path $vaultRoot '辅助\维护\Test-RuleTraceability.ps1') -VaultRoot $vaultRoot | Out-Host
    if (-not $?) { throw '规则溯源检查失败。' }
    & (Join-Path $vaultRoot '辅助\维护\Test-ActiveRuleSurface.ps1') -VaultRoot $vaultRoot | Out-Host
    if (-not $?) { throw '活动 Skill/规则面检查失败。' }
    & (Join-Path $vaultRoot '辅助\维护\Update-RuleEffectSummary.ps1') -VaultRoot $vaultRoot -ValidateOnly | Out-Host
    if (-not $?) { throw '规则效果目录检查失败。' }

    $report = [ordered]@{
        installedAt = (Get-Date).ToUniversalTime().ToString('o')
        kitGeneratedAt = [string]$kit.generatedAt
        vaultRoot = $vaultRoot
        productionWorkRoot = $workRoot
        tiktokSkuRoot = if ($SkipBusinessFiles) { $null } else { $skuRoot }
        tiktokWorkspaceRoot = if ($SkipBusinessFiles) { $null } else { $tiktokWorkspace }
        sevenSkillsRegistered = -not $SkipCodexRegistration
        userEnvironmentVariablesSet = -not $SkipUserEnvironmentVariables
        integrityPassed = $true
        businessFilesInstalled = -not $SkipBusinessFiles
        environmentsInstalled = $false
        credentialsMigrated = $false
        operationalRegressionPendingEnvironment = $true
        nextSteps = @(
            '安装 Codex 与需要的 Python/FFmpeg/Whisper/OCR 环境。',
            '重新安装并登录 HeyGen、ChatCut、飞书、店小秘、LinkFox 和浏览器。',
            '把新环境路径写入 Knowledge/辅助/配置/machine-paths.local.json。',
            '运行 Knowledge/辅助/维护/Test-OperationalKnowledge.ps1。',
            '完全退出并重启 Codex，然后新建对话。',
            '读取 Knowledge/辅助/自动任务/每日22点规则审计.md 并重建本机自动任务。'
        )
    }
    $reportDir = Join-Path $workRoot 'migration'
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    $reportPath = Join-Path $reportDir 'latest-install-report.json'
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding utf8
    $report | ConvertTo-Json -Depth 6
} finally {
    if (Test-Path -LiteralPath $stageRoot -PathType Container) {
        $resolvedStage = (Resolve-Path -LiteralPath $stageRoot).Path
        if ($resolvedStage.StartsWith($base + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -and
            (Split-Path -Leaf $resolvedStage).StartsWith('.knowledge-install-')) {
            Remove-Item -LiteralPath $resolvedStage -Recurse -Force
        }
    }
}
