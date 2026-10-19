[CmdletBinding()]
param([string]$VaultRoot)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($VaultRoot)) { $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path }
$registerPath = Join-Path $VaultRoot '资产\规则\活动规则总表.md'
$indexPath = Join-Path $VaultRoot '资产\规则\活动规则溯源索引.json'
$register = Get-Content -LiteralPath $registerPath -Encoding utf8
$index = Get-Content -LiteralPath $indexPath -Raw -Encoding utf8 | ConvertFrom-Json
$activeIds = @($register | ForEach-Object { if ($_ -match '^\| ([A-Z]+-[0-9]+) \| `active(?:_project)?` \|') { $Matches[1] } } | Sort-Object -Unique)
$direct = @($index.directEvidenceEntries.ruleId)
$legacy = @($index.legacyRegisterBasisOnly)
$covered = @($direct + $legacy | Sort-Object -Unique)
$missing = @($activeIds | Where-Object { $covered -notcontains $_ })
$orphan = @($covered | Where-Object { $activeIds -notcontains $_ })
$requiredDirect = @('SYS-012','IP-003','IP-006','COM-011','COM-012')
$missingRequiredDirect = @($requiredDirect | Where-Object { $direct -notcontains $_ })
$errors = @()
if ($missing.Count) { $errors += [ordered]@{ type='active_rules_without_trace_entry'; ids=$missing } }
if ($orphan.Count) { $errors += [ordered]@{ type='trace_entries_not_active'; ids=$orphan } }
if ($missingRequiredDirect.Count) { $errors += [ordered]@{ type='new_or_modified_rule_missing_direct_evidence'; ids=$missingRequiredDirect } }
$result = [ordered]@{
    checkedAt=(Get-Date).ToUniversalTime().ToString('o')
    activeRules=$activeIds.Count
    directEvidence=$direct.Count
    legacyBackfillPending=$legacy.Count
    warnings=if($legacy.Count){@([ordered]@{type='legacy_direct_evidence_backfill_pending';ids=$legacy})}else{@()}
    errors=$errors
    passed=($errors.Count -eq 0)
    automaticStatusChanges=$false
}
$result | ConvertTo-Json -Depth 6
if ($errors.Count) { throw 'Rule traceability regression failed.' }
