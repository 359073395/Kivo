[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RuleId,
    [Parameter(Mandatory)][ValidateSet('fact','execution','judgment','value','mixed')][string]$TaskType,
    [Parameter(Mandatory)][ValidateSet('changed','confirmed','rejected','prevented_error','no_material_effect')][string]$Effect,
    [Parameter(Mandatory)][string]$ObservableReason,
    [Parameter(Mandatory)][string]$TaskId,
    [string]$ProjectRef,
    [string]$SourceClient = 'codex',
    [string[]]$ArtifactRefs = @(),
    [string]$VaultRoot
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($VaultRoot)) { $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path }
$configPath = Join-Path $VaultRoot '辅助\配置\machine-paths.local.json'
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) { throw "Missing machine config: $configPath" }
$config = Get-Content -LiteralPath $configPath -Raw -Encoding utf8 | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace([string]$config.productionWorkRoot)) { throw 'productionWorkRoot is not configured.' }

$pending = Join-Path ([string]$config.productionWorkRoot) 'rule-effects\pending'
$null = New-Item -ItemType Directory -Force -Path $pending
$signalId = [guid]::NewGuid().ToString('D')
$record = [ordered]@{
    signalId = $signalId
    emittedAt = (Get-Date).ToUniversalTime().ToString('o')
    sourceClient = $SourceClient
    taskId = $TaskId
    projectRef = if ([string]::IsNullOrWhiteSpace($ProjectRef)) { $null } else { $ProjectRef }
    ruleId = $RuleId
    taskType = $TaskType
    effect = $Effect
    observableReason = $ObservableReason
    artifactRefs = @($ArtifactRefs)
    reviewStatus = 'pending'
}
$path = Join-Path $pending ("{0}_{1}.json" -f (Get-Date -Format 'yyyyMMdd_HHmmssfff'), $signalId)
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $path -Encoding utf8
[ordered]@{ written = $true; path = $path; signalId = $signalId; portable = $false } | ConvertTo-Json -Depth 3
