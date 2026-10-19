[CmdletBinding()]
param([string]$VaultRoot)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($VaultRoot)) { $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path }
$fixturePath = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\decision-audit-fixtures.json'
$data = Get-Content -LiteralPath $fixturePath -Raw -Encoding utf8 | ConvertFrom-Json
$expected = [ordered]@{
    'AUDIT-FACT'='pass_direct'
    'AUDIT-EMPTY'='fail_and_recheck_route'
    'AUDIT-UNSUPPORTED'='reject_action'
    'AUDIT-FAKE-PARALLEL'='redo_problem_definition'
    'AUDIT-COMPACT-ESCAPE'='upgrade_full'
    'AUDIT-VALUE-FLIP'='user_value_choice'
    'AUDIT-IRREVERSIBLE'='precommit_path'
}
$errors = @()
foreach ($entry in $expected.GetEnumerator()) {
    $fixture = @($data.fixtures | Where-Object id -eq $entry.Key)
    if ($fixture.Count -ne 1) { $errors += [ordered]@{type='missing_or_duplicate_fixture';id=$entry.Key}; continue }
    if ([string]$fixture[0].expected -ne [string]$entry.Value) { $errors += [ordered]@{type='wrong_expected_contract';id=$entry.Key;expected=$entry.Value;actual=$fixture[0].expected} }
    if ([string]::IsNullOrWhiteSpace([string]$fixture[0].observableCheck)) { $errors += [ordered]@{type='missing_observable_check';id=$entry.Key} }
}
$result=[ordered]@{
    testType='audit_fixture_contract_only'
    checkedAt=(Get-Date).ToUniversalTime().ToString('o')
    fixtures=@($data.fixtures).Count
    errors=$errors
    passed=($errors.Count -eq 0)
    modelSemanticExecution=$false
    crossModelReview=$false
}
$result | ConvertTo-Json -Depth 5
if($errors.Count){throw 'Decision audit fixture contract failed.'}
