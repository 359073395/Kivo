[CmdletBinding()]
param([string]$VaultRoot)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
}

$paths = [ordered]@{
    skill = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\SKILL.md'
    protocol = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\references\deep-reasoning-protocol.md'
    rules = Join-Path $VaultRoot '资产\规则\活动规则总表.md'
    governance = Join-Path $VaultRoot '资产\规则\规则权威与变更协议.md'
    framework = Join-Path $VaultRoot '资产\方法论\知识库思考框架与运行流程.md'
    cards = Join-Path $VaultRoot '资产\方法论\第一性原理决策系统\method_cards.json'
    maoCards = Join-Path $VaultRoot '资产\方法论\毛选方法论决策系统\method_cards.json'
    cases = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\deep-reasoning-behavior-cases.json'
    auditSchema = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\decision-audit-record.schema.json'
    fixtures = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\decision-audit-fixtures.json'
    acceptance = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\BEHAVIOR-ACCEPTANCE.md'
    fixtureTest = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\Test-DecisionAuditFixtures.ps1'
}
$errors = [System.Collections.Generic.List[object]]::new()
foreach ($entry in $paths.GetEnumerator()) {
    if (-not (Test-Path -LiteralPath $entry.Value -PathType Leaf)) {
        $errors.Add([ordered]@{ type = 'missing'; name = $entry.Key; path = $entry.Value })
    }
}

if ($errors.Count -eq 0) {
    $skillText = Get-Content -LiteralPath $paths.skill -Raw -Encoding utf8
    $protocolText = Get-Content -LiteralPath $paths.protocol -Raw -Encoding utf8
    $ruleText = Get-Content -LiteralPath $paths.rules -Raw -Encoding utf8
    $governanceText = Get-Content -LiteralPath $paths.governance -Raw -Encoding utf8
    $frameworkText = Get-Content -LiteralPath $paths.framework -Raw -Encoding utf8
    $cardData = Get-Content -LiteralPath $paths.cards -Raw -Encoding utf8 | ConvertFrom-Json
    $maoData = Get-Content -LiteralPath $paths.maoCards -Raw -Encoding utf8 | ConvertFrom-Json
    $caseData = Get-Content -LiteralPath $paths.cases -Raw -Encoding utf8 | ConvertFrom-Json
    $null = Get-Content -LiteralPath $paths.auditSchema -Raw -Encoding utf8 | ConvertFrom-Json
    $fixtureData = Get-Content -LiteralPath $paths.fixtures -Raw -Encoding utf8 | ConvertFrom-Json

    foreach ($id in @('SYS-012','IP-003','IP-004','IP-005','IP-006')) {
        $activePattern = '\| {0} \| `active`' -f [regex]::Escape($id)
        if ($ruleText -notmatch $activePattern) {
            $errors.Add([ordered]@{ type = 'active-rule-missing'; id = $id })
        }
    }
    foreach ($needle in @('纯事实/知识','纯执行','价值翻转','紧凑模式资格','no_material_effect','prevented_error','unrelated','不可逆或无直接反馈','临时有界豁免')) {
        if ($protocolText -notmatch [regex]::Escape($needle)) {
            $errors.Add([ordered]@{ type = 'missing-protocol-surface'; value = $needle })
        }
    }
    foreach ($needle in @('活动规则编译门','provenance','verification','governanceStatus','不得自动修改活动状态')) {
        if ($governanceText -notmatch [regex]::Escape($needle)) {
            $errors.Add([ordered]@{ type = 'missing-governance-surface'; value = $needle })
        }
    }
    foreach ($needle in @('纯事实/知识','价值拆分使用翻转判据','紧凑路径必须同时满足','无条件升级完整闭环','一次性、不可逆')) {
        if ($frameworkText -notmatch [regex]::Escape($needle)) {
            $errors.Add([ordered]@{ type = 'missing-framework-surface'; value = $needle })
        }
    }
    foreach ($needle in @('objective compact/deep qualification gate','no_material_effect','irreversible/no-feedback decisions')) {
        if ($skillText -notmatch [regex]::Escape($needle)) {
            $errors.Add([ordered]@{ type = 'missing-skill-surface'; value = $needle })
        }
    }
    if ([int]$cardData.schemaVersion -lt 4) { $errors.Add([ordered]@{ type = 'first-principles-schema-too-old' }) }
    foreach ($id in @('SYS-012','IP-003','IP-004','IP-005','IP-006')) {
        if (@($cardData.activeRuleIds) -notcontains $id) { $errors.Add([ordered]@{ type = 'card-rule-missing'; id = $id }) }
    }
    if (@($cardData.cards).Count -ne 3) { $errors.Add([ordered]@{ type = 'invalid-fixed-checkpoint-count'; count = @($cardData.cards).Count }) }
    if ([string]$maoData.format -ne 'maoxuan-decision-method-cards-v2') { $errors.Add([ordered]@{ type = 'mao-schema-too-old' }) }
    $m07 = @($maoData.cards | Where-Object id -eq 'M07')[0]
    $m09 = @($maoData.cards | Where-Object id -eq 'M09')[0]
    if (-not @($m07.sourceAnchors | Where-Object { $_.verification -eq 'incorrect_anchor' -and $_.ocrPageMarkers -eq '26' })) { $errors.Add([ordered]@{ type = 'm07-old-anchor-not-marked' }) }
    if (-not @($m07.sourceAnchors | Where-Object { $_.verification -eq 'original_scan_reviewed' -and $_.ocrPageMarkers -eq '22-23' -and $_.printedPages -eq '1132-1133' })) { $errors.Add([ordered]@{ type = 'm07-correct-anchor-missing' }) }
    if (-not @($m09.sourceAnchors | Where-Object { $_.verification -eq 'original_scan_reviewed' -and $_.ocrPageMarkers -eq '316-317' -and $_.printedPages -eq '1096-1097' })) { $errors.Add([ordered]@{ type = 'm09-precise-anchor-missing' }) }
    foreach ($id in 1..17 | ForEach-Object { 'DEEP-{0:D2}' -f $_ }) {
        if (@($caseData.cases.id) -notcontains $id) { $errors.Add([ordered]@{ type = 'behavior-case-missing'; id = $id }) }
    }
    if (@($fixtureData.fixtures).Count -lt 7) { $errors.Add([ordered]@{ type = 'insufficient-audit-fixtures'; count = @($fixtureData.fixtures).Count }) }
}

$result = [ordered]@{
    testType = 'structural_regression_only'
    checkedAt = (Get-Date).ToUniversalTime().ToString('o')
    declaredBehaviorCases = if (Test-Path -LiteralPath $paths.cases) { @((Get-Content -LiteralPath $paths.cases -Raw -Encoding utf8 | ConvertFrom-Json).cases).Count } else { 0 }
    errors = @($errors)
    passed = ($errors.Count -eq 0)
    semanticBehaviorCertified = $false
}
$result | ConvertTo-Json -Depth 6
if ($errors.Count -gt 0) { throw 'Deep reasoning structural regression failed.' }
