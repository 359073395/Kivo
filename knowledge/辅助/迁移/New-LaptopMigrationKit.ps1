[CmdletBinding()]
param(
    [string]$VaultRoot,
    [string]$OutputRoot = 'D:\Knowledge-Backups',
    [string]$Timestamp = (Get-Date -Format 'yyyyMMdd_HHmm')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

if ([string]::IsNullOrWhiteSpace($VaultRoot)) { $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path }
else { $VaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path }
$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$kitRoot = Join-Path $OutputRoot "Knowledge-LaptopKit_$Timestamp"
if (Test-Path -LiteralPath $kitRoot) { throw "套件目录已存在：$kitRoot" }
New-Item -ItemType Directory -Path $kitRoot | Out-Null
$stageRoot = Join-Path $OutputRoot ('.laptop-kit-stage-' + [guid]::NewGuid().ToString('N'))
if (-not $stageRoot.StartsWith($OutputRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) { throw '临时目录越出备份根目录。' }
New-Item -ItemType Directory -Path $stageRoot | Out-Null

$allowedExtensions = @(
    '.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.json', '.ndjson', '.jsonl',
    '.md', '.txt', '.srt', '.html', '.docx', '.pdf', '.png', '.jpg', '.jpeg',
    '.webp', '.gif', '.py', '.ps1', '.cmd', '.mjs', '.js', '.yaml', '.yml'
)
$excludedSegments = @(
    '.git', '.venv', 'venv', 'node_modules', '__pycache__', '_runtime', '.codex_temp',
    '.codex_tmp', '.codex-tmp', 'edge_profile', 'pydeps', 'temp', 'tmp', 'scratch',
    '_recycle_pending', 'rule-effects'
)

function Get-Sha256([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

function Copy-SelectedFiles([string]$SourceRoot, [string]$DestinationRoot, [string]$Profile) {
    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) { return [ordered]@{ profile=$Profile; source=$SourceRoot; files=0; bytes=0 } }
    $count = 0
    $bytes = [int64]0
    foreach ($file in Get-ChildItem -LiteralPath $SourceRoot -Recurse -File -Force -ErrorAction Stop) {
        if ($allowedExtensions -notcontains $file.Extension.ToLowerInvariant()) { continue }
        $relative = [System.IO.Path]::GetRelativePath($SourceRoot, $file.FullName)
        $segments = @($relative -split '[\\/]')
        if (@($segments | Where-Object { $excludedSegments -contains $_ }).Count -gt 0) { continue }
        if ($file.Name -match '(?i)^\.env|cookies?|login data|credential|password|passwd|oauth|api[_-]?key|access[_-]?token|refresh[_-]?token|feishu_auth') { continue }
        if ($Profile -eq 'sku' -and $segments[0] -eq '05_可移植Skill') { continue }
        $destination = Join-Path $DestinationRoot $relative
        New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
        [System.IO.File]::Copy($file.FullName, $destination, $false)
        $count++
        $bytes += $file.Length
    }
    [ordered]@{ profile=$Profile; source=$SourceRoot; files=$count; bytes=$bytes }
}

function Write-PayloadManifest([string]$Root, [string]$Kind, $Selection) {
    $selectionPath = Join-Path $Root 'DATA-SELECTION.json'
    [ordered]@{
        generatedAt = (Get-Date).ToUniversalTime().ToString('o')
        profiles = $Selection
        includedExtensions = $allowedExtensions
        excludedPathSegments = $excludedSegments
        excludesSecrets = $true
        excludesVideoAudioArchivesAndSoftwareEnvironments = $true
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $selectionPath -Encoding utf8
    $files = Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        Where-Object Name -ne 'PAYLOAD-MANIFEST.json' |
        Sort-Object FullName |
        ForEach-Object { [ordered]@{ path=[System.IO.Path]::GetRelativePath($Root,$_.FullName); bytes=$_.Length; sha256=Get-Sha256 $_.FullName } }
    $manifest = [ordered]@{ schemaVersion=1; kind=$Kind; generatedAt=(Get-Date).ToUniversalTime().ToString('o'); fileCount=@($files).Count; files=@($files) }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Root 'PAYLOAD-MANIFEST.json') -Encoding utf8
    $manifest
}

function New-ZipFromDirectory([string]$SourceRoot, [string]$DestinationZip, [System.IO.Compression.CompressionLevel]$Level) {
    $stream = [System.IO.File]::Open($DestinationZip,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
    try {
        $archive=[System.IO.Compression.ZipArchive]::new($stream,[System.IO.Compression.ZipArchiveMode]::Create,$true)
        try {
            foreach($file in Get-ChildItem -LiteralPath $SourceRoot -Recurse -File -Force | Sort-Object FullName){
                $name=[System.IO.Path]::GetRelativePath($SourceRoot,$file.FullName).Replace('\','/')
                $entry=$archive.CreateEntry($name,$Level)
                $input=[System.IO.File]::OpenRead($file.FullName)
                try{$output=$entry.Open();try{$input.CopyTo($output)}finally{$output.Dispose()}}finally{$input.Dispose()}
            }
        } finally { $archive.Dispose() }
    } finally { $stream.Dispose() }
}

function New-CoreZip([string]$DestinationZip) {
    $manifestPath=Join-Path $VaultRoot 'PORTABLE-MANIFEST.json'
    $manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
    $stream=[System.IO.File]::Open($DestinationZip,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
    try{
        $archive=[System.IO.Compression.ZipArchive]::new($stream,[System.IO.Compression.ZipArchiveMode]::Create,$true)
        try{
            $records=@([pscustomobject]@{path='PORTABLE-MANIFEST.json';full=$manifestPath})
            foreach($item in @($manifest.files)){$records += [pscustomobject]@{path=([string]$item.path).Replace('\','/');full=Join-Path $VaultRoot ([string]$item.path)}}
            foreach($record in $records){$entry=$archive.CreateEntry($record.path,[System.IO.Compression.CompressionLevel]::Optimal);$input=[System.IO.File]::OpenRead($record.full);try{$output=$entry.Open();try{$input.CopyTo($output)}finally{$output.Dispose()}}finally{$input.Dispose()}}
        }finally{$archive.Dispose()}
    }finally{$stream.Dispose()}
}

function New-FileRecord([string]$Path,[string]$Type){$item=Get-Item -LiteralPath $Path;[ordered]@{name=$item.Name;type=$Type;bytes=$item.Length;sha256=Get-Sha256 $item.FullName}}

try {
    & (Join-Path $VaultRoot '辅助\迁移\Verify-PortableManifest.ps1') -VaultRoot $VaultRoot -FailOnUntracked | Out-Host
    if (-not $?) { throw '便携清单严格验证失败。' }
    $config=Get-Content -LiteralPath (Join-Path $VaultRoot '辅助\配置\machine-paths.local.json') -Raw -Encoding utf8 | ConvertFrom-Json
    $skuSource=[string]$config.tiktokSkuRoot
    $productionSource=[string]$config.productionWorkRoot
    $tiktokSource=[string]$config.tiktokWorkspaceRoot
    foreach($required in @($skuSource,$productionSource,$tiktokSource)){if([string]::IsNullOrWhiteSpace($required)-or -not(Test-Path -LiteralPath $required -PathType Container)){throw "业务文件根目录缺失：$required"}}

    $coreZip=Join-Path $kitRoot "Knowledge_${Timestamp}_portable.zip"
    New-CoreZip $coreZip

    $businessStage=Join-Path $stageRoot 'business'
    New-Item -ItemType Directory -Path $businessStage | Out-Null
    $selection=[System.Collections.Generic.List[object]]::new()
    $selection.Add((Copy-SelectedFiles $skuSource (Join-Path $businessStage 'TikTokSKU') 'sku'))
    $selection.Add((Copy-SelectedFiles $productionSource (Join-Path $businessStage 'ProductionWork') 'production-work'))
    $selection.Add((Copy-SelectedFiles $tiktokSource (Join-Path $businessStage 'TikTokWorkspace') 'tiktok-workspace'))
    $businessManifest=Write-PayloadManifest $businessStage 'portable-business-files' @($selection)
    $businessZip=Join-Path $kitRoot "Knowledge_BusinessFiles_${Timestamp}.zip"
    New-ZipFromDirectory $businessStage $businessZip ([System.IO.Compression.CompressionLevel]::Fastest)

    Copy-Item -LiteralPath (Join-Path $VaultRoot '辅助\迁移\INSTALL-ON-LAPTOP.ps1') -Destination (Join-Path $kitRoot 'INSTALL-ON-LAPTOP.ps1')
    Copy-Item -LiteralPath (Join-Path $VaultRoot '辅助\迁移\笔记本一键迁移.md') -Destination (Join-Path $kitRoot 'README-笔记本迁移.md')
    $coreRecord=New-FileRecord $coreZip 'knowledge-core'
    $businessRecord=New-FileRecord $businessZip 'business-files'
    $installerRecord=New-FileRecord (Join-Path $kitRoot 'INSTALL-ON-LAPTOP.ps1') 'installer'
    $guideRecord=New-FileRecord (Join-Path $kitRoot 'README-笔记本迁移.md') 'guide'
    $coreManifest=Get-Content -LiteralPath (Join-Path $VaultRoot 'PORTABLE-MANIFEST.json') -Raw -Encoding utf8 | ConvertFrom-Json
    $businessBytes=[int64]0
    foreach($businessFile in @($businessManifest.files)){$businessBytes += [int64]$businessFile['bytes']}
    $kitManifest=[ordered]@{
        schemaVersion=1
        generatedAt=(Get-Date).ToUniversalTime().ToString('o')
        oneCommand='pwsh -NoProfile -ExecutionPolicy Bypass -File .\INSTALL-ON-LAPTOP.ps1'
        files=[ordered]@{core=$coreRecord;businessFiles=$businessRecord;installer=$installerRecord;guide=$guideRecord}
        contents=[ordered]@{
            knowledgeTrackedFiles=@($coreManifest.files).Count
            businessFiles=@($businessManifest.files).Count
            businessBytes=$businessBytes
            activeSkills=7
            secretsIncluded=$false
        }
        included=@('Knowledge complete portable vault','seven active knowledge Skills','TikTokSKU Excel and operational files','non-media production files and project state','safe TikTok workspace data and scripts')
        excluded=@('Python/FFmpeg/Whisper/OCR and other software environments','API keys/OAuth/cookies/passwords/browser profiles','MP4/MP3/WAV/ZIP and editing projects','Codex automation enablement state')
    }
    $kitManifestPath=Join-Path $kitRoot 'MIGRATION-KIT.json'
    $kitManifest|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $kitManifestPath -Encoding utf8
    $sumLines=foreach($path in @($coreZip,$businessZip,(Join-Path $kitRoot 'INSTALL-ON-LAPTOP.ps1'),(Join-Path $kitRoot 'README-笔记本迁移.md'),$kitManifestPath)){"$(Get-Sha256 $path)  $([System.IO.Path]::GetFileName($path))"}
    $sumLines|Set-Content -LiteralPath (Join-Path $kitRoot 'SHA256SUMS.txt') -Encoding utf8
    [ordered]@{kitRoot=$kitRoot;oneCommand=[string]$kitManifest.oneCommand;core=$coreRecord;businessFiles=$businessRecord;businessFileCount=@($businessManifest.files).Count;businessBytes=[int64]$kitManifest.contents.businessBytes;secretsIncluded=$false}|ConvertTo-Json -Depth 7
} catch {
    if(Test-Path -LiteralPath $kitRoot -PathType Container){$resolvedKit=(Resolve-Path -LiteralPath $kitRoot).Path;if($resolvedKit.StartsWith($OutputRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)-and(Split-Path -Leaf $resolvedKit).StartsWith('Knowledge-LaptopKit_')){Remove-Item -LiteralPath $resolvedKit -Recurse -Force}}
    throw
} finally {
    if(Test-Path -LiteralPath $stageRoot -PathType Container){$resolvedStage=(Resolve-Path -LiteralPath $stageRoot).Path;if($resolvedStage.StartsWith($OutputRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)-and(Split-Path -Leaf $resolvedStage).StartsWith('.laptop-kit-stage-')){Remove-Item -LiteralPath $resolvedStage -Recurse -Force}}
}
