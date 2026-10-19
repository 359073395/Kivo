[CmdletBinding()]
param([string]$VaultRoot, [switch]$ValidateOnly)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($VaultRoot)) { $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path }
$configPath = Join-Path $VaultRoot '辅助\配置\machine-paths.local.json'
$schemaPath = Join-Path $VaultRoot '辅助\规则效果\schema.json'
$aggregatePath = Join-Path $VaultRoot '辅助\规则效果\规则效果聚合.json'
$candidatePath = Join-Path $VaultRoot '辅助\规则效果\规则审查候选.md'
foreach ($path in @($configPath,$schemaPath,$aggregatePath,$candidatePath)) { if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required file: $path" } }

$null = Get-Content -LiteralPath $schemaPath -Raw -Encoding utf8 | ConvertFrom-Json
$config = Get-Content -LiteralPath $configPath -Raw -Encoding utf8 | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace([string]$config.productionWorkRoot)) { throw 'productionWorkRoot is not configured.' }
$pending = Join-Path ([string]$config.productionWorkRoot) 'rule-effects\pending'
if (-not (Test-Path -LiteralPath $pending)) { $null = New-Item -ItemType Directory -Force -Path $pending }

$allowedTaskTypes = @('fact','execution','judgment','value','mixed')
$allowedEffects = @('changed','confirmed','rejected','prevented_error','no_material_effect')
$signals = [System.Collections.Generic.List[object]]::new()
$errors = [System.Collections.Generic.List[object]]::new()
foreach ($file in @(Get-ChildItem -LiteralPath $pending -Filter '*.json' -File -ErrorAction SilentlyContinue)) {
    try { $signal = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8 | ConvertFrom-Json }
    catch { $errors.Add([ordered]@{ file = $file.FullName; error = 'invalid_json' }); continue }
    foreach ($required in @('signalId','emittedAt','sourceClient','taskId','ruleId','taskType','effect','observableReason','artifactRefs','reviewStatus')) {
        if ($null -eq $signal.PSObject.Properties[$required]) { $errors.Add([ordered]@{ file = $file.FullName; error = 'missing_field'; field = $required }) }
    }
    foreach ($requiredText in @('signalId','emittedAt','sourceClient','taskId','ruleId','taskType','effect','observableReason','reviewStatus')) {
        if ([string]::IsNullOrWhiteSpace([string]$signal.$requiredText)) { $errors.Add([ordered]@{ file = $file.FullName; error = 'blank_field'; field = $requiredText }) }
    }
    if ($allowedTaskTypes -notcontains [string]$signal.taskType) { $errors.Add([ordered]@{ file = $file.FullName; error = 'invalid_task_type' }) }
    if ($allowedEffects -notcontains [string]$signal.effect) { $errors.Add([ordered]@{ file = $file.FullName; error = 'invalid_effect' }) }
    $signals.Add($signal)
}
if ($errors.Count -gt 0) {
    [ordered]@{ passed = $false; errors = @($errors) } | ConvertTo-Json -Depth 6
    throw 'Rule effect signal validation failed.'
}

$aggregate = Get-Content -LiteralPath $aggregatePath -Raw -Encoding utf8 | ConvertFrom-Json
$processed = @{}; foreach ($id in @($aggregate.processedSignalIds)) { $processed[[string]$id] = $true }
$newSignals = @($signals | Where-Object { -not $processed.ContainsKey([string]$_.signalId) })
if ($ValidateOnly -or $newSignals.Count -eq 0) {
    [ordered]@{ passed = $true; validateOnly = [bool]$ValidateOnly; pendingFiles = $signals.Count; newSignals = $newSignals.Count; changed = $false; pendingPath = $pending } | ConvertTo-Json -Depth 4
    return
}

$rows = @{}; foreach ($row in @($aggregate.rules)) { $rows[[string]$row.ruleId] = [ordered]@{ ruleId=[string]$row.ruleId; taskRefs=@($row.taskRefs); effects=[ordered]@{ changed=[int]$row.effects.changed; confirmed=[int]$row.effects.confirmed; rejected=[int]$row.effects.rejected; prevented_error=[int]$row.effects.prevented_error; no_material_effect=[int]$row.effects.no_material_effect }; lastSignalAt=[string]$row.lastSignalAt; signalIds=@($row.signalIds) } }
foreach ($signal in $newSignals) {
    $id=[string]$signal.ruleId
    if (-not $rows.ContainsKey($id)) { $rows[$id]=[ordered]@{ ruleId=$id; taskRefs=@(); effects=[ordered]@{ changed=0; confirmed=0; rejected=0; prevented_error=0; no_material_effect=0 }; lastSignalAt=$null; signalIds=@() } }
    $taskRef = if ([string]::IsNullOrWhiteSpace([string]$signal.projectRef)) { [string]$signal.taskId } else { "{0}|{1}" -f $signal.taskId,$signal.projectRef }
    $rows[$id].taskRefs = @($rows[$id].taskRefs + $taskRef | Sort-Object -Unique)
    $rows[$id].effects[[string]$signal.effect] = [int]$rows[$id].effects[[string]$signal.effect] + 1
    $rows[$id].lastSignalAt = if ($signal.emittedAt -is [datetime]) { $signal.emittedAt.ToUniversalTime().ToString('o') } else { [string]$signal.emittedAt }
    $rows[$id].signalIds = @($rows[$id].signalIds + [string]$signal.signalId | Sort-Object -Unique)
    $processed[[string]$signal.signalId] = $true
}
$newAggregate = [ordered]@{ schemaVersion=1; generatedAt=(Get-Date).ToUniversalTime().ToString('o'); processedSignalIds=@($processed.Keys | Sort-Object); rules=@($rows.Values | Sort-Object ruleId) }
$newAggregate | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $aggregatePath -Encoding utf8

$candidates = @($rows.Values | Where-Object {
    @($_.taskRefs).Count -gt 1 -and [int]$_.effects.no_material_effect -gt 0 -and
    ([int]$_.effects.changed + [int]$_.effects.confirmed + [int]$_.effects.rejected + [int]$_.effects.prevented_error) -eq 0
})
$lines = [System.Collections.Generic.List[string]]::new(); $lines.Add('# 规则审查候选'); $lines.Add('');
if ($candidates.Count -eq 0) { $lines.Add('当前没有由跨任务规则效果信号触发的审查候选。') }
else { $lines.Add('| 规则 | 跨任务证据 | 建议动作 |'); $lines.Add('|---|---|---|'); foreach($row in $candidates){ $lines.Add("| $($row.ruleId) | 不同任务只出现 `no_material_effect`，且未见改变/确认/否决/阻止错误 | 人工检查是否应合并、修改、替代或停用；不得自动变更状态 |") } }
$lines.Add(''); $lines.Add('> 本页只触发人工审查，不自动停用、降级、合并或替代任何活动规则。')
$lines | Set-Content -LiteralPath $candidatePath -Encoding utf8
[ordered]@{ passed=$true; validateOnly=$false; pendingFiles=$signals.Count; newSignals=$newSignals.Count; changed=$true; reviewCandidates=$candidates.Count; pendingPath=$pending } | ConvertTo-Json -Depth 4
