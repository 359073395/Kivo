param(
    [Parameter(Mandatory = $true)]
    [string]$Title,

    [ValidateSet('TikTok', '跨境电商', '个人IP', '知识库', '其他')]
    [string]$Category = '其他',

    [string]$VaultRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-SafeName {
    param([string]$Value)
    $invalid = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Value.Trim()
    foreach ($char in $invalid) {
        $safe = $safe.Replace([string]$char, '_')
    }
    $safe = $safe -replace '\s+', '_'
    $safe = $safe.Trim('.', '_')
    if ([string]::IsNullOrWhiteSpace($safe)) {
        throw 'Title becomes empty after filename sanitization.'
    }
    return $safe
}

if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $skillRoot = Split-Path -Parent $PSScriptRoot
    $skillContainer = Split-Path -Parent $skillRoot
    $resolvedVaultRoot = Split-Path -Parent $skillContainer
} else {
    $resolvedVaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path
}

$marker = Join-Path $resolvedVaultRoot 'knowledge-base.json'
if (-not (Test-Path -LiteralPath $marker)) {
    throw "Not a knowledge vault: $resolvedVaultRoot"
}

$safeTitle = ConvertTo-SafeName -Value $Title
$now = Get-Date
$handoffRoot = Join-Path $resolvedVaultRoot '项目\会话交接'
$categoryRoot = Join-Path $handoffRoot $Category
$yearRoot = Join-Path $categoryRoot $now.ToString('yyyy')
$folderName = '{0}_{1}' -f $now.ToString('yyyyMMdd_HHmmss'), $safeTitle
$handoffFolder = Join-Path $yearRoot $folderName

if (Test-Path -LiteralPath $handoffFolder) {
    throw "Handoff folder already exists: $handoffFolder"
}

New-Item -ItemType Directory -Path $handoffFolder -Force | Out-Null

$metadata = [ordered]@{
    schemaVersion = 1
    title = $Title
    category = $Category
    createdAt = $now.ToString('o')
    status = 'draft'
    source = 'selected-codex-conversation'
    rawTranscriptIncluded = $false
    containsSecrets = $false
    vaultRelativePath = [System.IO.Path]::GetRelativePath($resolvedVaultRoot, $handoffFolder).Replace('\', '/')
}

$metadataPath = Join-Path $handoffFolder 'metadata.json'
$metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $metadataPath -Encoding utf8

$handoffTemplate = @"
# $Title

## 目的与范围

待填写。

## 当前进度

待填写。

## 已确认决定与最新规则

待填写。

## 关键文件与路径

待填写。大型素材只记录外部路径、哈希、状态和恢复条件。

## 使用的 Skill、工具与外部依赖

待填写。

## 已完成验证

待填写。

## 未完成事项与下一步

待填写。

## 风险、停止条件与恢复注意事项

待填写。不得写入密码、Cookie、API Key、访问令牌或私人登录信息。
"@

$handoffPath = Join-Path $handoffFolder 'HANDOFF.md'
Set-Content -LiteralPath $handoffPath -Value $handoffTemplate -Encoding utf8

Write-Output $handoffFolder
