[CmdletBinding()]
param(
    [string]$VaultRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($VaultRoot)) {
    $VaultRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
} else {
    $VaultRoot = (Resolve-Path -LiteralPath $VaultRoot).Path
}

$errors = [System.Collections.Generic.List[object]]::new()
$warnings = [System.Collections.Generic.List[object]]::new()
$configPath = Join-Path $VaultRoot '辅助\配置\machine-paths.local.json'
$routerPath = Join-Path $VaultRoot 'skill\tiktok-content-system\modules\pure-heygen\scripts\workspace_state.py'
$testPath = Join-Path $VaultRoot 'skill\tiktok-content-system\modules\pure-heygen\tests\test_workspace_state.py'
$presenterImageGateTestPath = Join-Path $VaultRoot 'skill\tiktok-content-system\modules\pure-heygen\tests\test_presenter_image_gate.py'
$remoteInputGateTestPath = Join-Path $VaultRoot 'skill\tiktok-content-system\modules\pure-heygen\tests\test_remote_input_gate.py'
$cleanupRejectedMediaTestPath = Join-Path $VaultRoot 'skill\tiktok-content-system\modules\pure-heygen\tests\test_cleanup_rejected_media.py'
$methodPath = Join-Path $VaultRoot '资产\带货视频\纯HeyGen数字人口播已验证生产方法_2026-08-29.md'
$rulePath = Join-Path $VaultRoot '资产\规则\活动规则总表.md'
$deepReasoningTestPath = Join-Path $VaultRoot 'skill\ip-commerce-decision-system\tests\Test-DeepReasoningProtocol.ps1'
$flashPriceTestPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\sku-feishu\tests\test_flash_price_rules.py'
$flashIntegrityTestPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\sku-feishu\tests\test_flash_ooxml_integrity.py'
$warehouseSourceValidatorPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\sku-feishu\scripts\validate_current_warehouse_source.py'
$warehouseSourceTestPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\sku-feishu\tests\test_current_warehouse_source.py'
$selectionEvidenceTestPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\selection-engine\tests\test_market_evidence.py'
$linkDispositionTestPath = Join-Path $VaultRoot 'skill\tiktok-commerce-operations\modules\listing-optimization\tests\test_link_disposition_rules.py'

foreach ($required in @($configPath, $routerPath, $testPath, $presenterImageGateTestPath, $remoteInputGateTestPath, $cleanupRejectedMediaTestPath, $methodPath, $rulePath, $deepReasoningTestPath, $flashPriceTestPath, $flashIntegrityTestPath, $warehouseSourceValidatorPath, $warehouseSourceTestPath, $selectionEvidenceTestPath, $linkDispositionTestPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        $errors.Add([ordered]@{ type = 'missing-required-file'; path = $required })
    }
}

$pythonPath = $null
$productionRoot = $null
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    $config = Get-Content -LiteralPath $configPath -Raw -Encoding utf8 | ConvertFrom-Json
    $productionRoot = [string]$config.productionWorkRoot
    if ([string]::IsNullOrWhiteSpace($productionRoot)) {
        $errors.Add([ordered]@{ type = 'blank-production-work-root' })
    } elseif (-not (Test-Path -LiteralPath $productionRoot -PathType Container)) {
        $errors.Add([ordered]@{ type = 'missing-production-work-root'; value = $productionRoot })
    }

    $configuredPython = [string]$config.videoTranscriptPython
    if (-not [string]::IsNullOrWhiteSpace($configuredPython) -and (Test-Path -LiteralPath $configuredPython -PathType Leaf)) {
        $pythonPath = $configuredPython
    }
}

if ($null -eq $pythonPath) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $pythonCommand) {
        $pythonPath = $pythonCommand.Source
    } else {
        $errors.Add([ordered]@{ type = 'python-not-found' })
    }
}

$unitTestResult = $null
$presenterImageGateTestResult = $null
$remoteInputGateTestResult = $null
$cleanupRejectedMediaTestResult = $null
$flashPriceTestResult = $null
$flashIntegrityTestResult = $null
$warehouseSourceTestResult = $null
$warehouseSourceCheckResult = $null
$warehouseFlashGateResult = $null
$selectionEvidenceTestResult = $null
$linkDispositionTestResult = $null
$flashPythonPath = $pythonPath
$recoveryResult = $null
$junctionResolution = $null
if ($errors.Count -eq 0) {
    $env:PYTHONDONTWRITEBYTECODE = '1'

    $flashDependencyProbe = & $flashPythonPath -c "import lxml, openpyxl" 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $codexRuntimePython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (Test-Path -LiteralPath $codexRuntimePython -PathType Leaf) {
            $runtimeProbe = & $codexRuntimePython -c "import lxml, openpyxl" 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0) {
                $flashPythonPath = $codexRuntimePython
            } else {
                $errors.Add([ordered]@{ type = 'flash-test-python-dependencies-missing'; output = $runtimeProbe.Trim() })
            }
        } else {
            $errors.Add([ordered]@{ type = 'flash-test-python-not-found'; attempted = $codexRuntimePython; output = $flashDependencyProbe.Trim() })
        }
    }

    $unitOutput = & $pythonPath $testPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'pure-heygen-behavior-tests-failed'; output = $unitOutput.Trim() })
    } else {
        $unitTestResult = $unitOutput.Trim()
    }

    $presenterImageGateOutput = & $pythonPath $presenterImageGateTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'presenter-image-gate-tests-failed'; output = $presenterImageGateOutput.Trim() })
    } else {
        $presenterImageGateTestResult = $presenterImageGateOutput.Trim()
    }

    $remoteInputGateOutput = & $pythonPath $remoteInputGateTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'remote-input-gate-tests-failed'; output = $remoteInputGateOutput.Trim() })
    } else {
        $remoteInputGateTestResult = $remoteInputGateOutput.Trim()
    }

    $cleanupRejectedMediaOutput = & $pythonPath $cleanupRejectedMediaTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'cleanup-rejected-media-tests-failed'; output = $cleanupRejectedMediaOutput.Trim() })
    } else {
        $cleanupRejectedMediaTestResult = $cleanupRejectedMediaOutput.Trim()
    }

    $flashPriceOutput = & $flashPythonPath $flashPriceTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'flash-price-behavior-tests-failed'; output = $flashPriceOutput.Trim() })
    } else {
        $flashPriceTestResult = $flashPriceOutput.Trim()
    }

    $flashIntegrityOutput = & $flashPythonPath $flashIntegrityTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'flash-ooxml-integrity-tests-failed'; output = $flashIntegrityOutput.Trim() })
    } else {
        $flashIntegrityTestResult = $flashIntegrityOutput.Trim()
    }

    $warehouseSourceTestOutput = & $pythonPath $warehouseSourceTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'warehouse-source-tests-failed'; output = $warehouseSourceTestOutput.Trim() })
    } else {
        $warehouseSourceTestResult = $warehouseSourceTestOutput.Trim()
    }

    $warehouseSourceOutput = & $pythonPath $warehouseSourceValidatorPath --vault-root $VaultRoot --mode source-read 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'current-warehouse-source-check-failed'; output = $warehouseSourceOutput.Trim() })
    } else {
        try {
            $warehouseSourceCheckResult = $warehouseSourceOutput | ConvertFrom-Json
            if (-not [bool]$warehouseSourceCheckResult.allowed -or -not [bool]$warehouseSourceCheckResult.sourceHashVerified) {
                $errors.Add([ordered]@{ type = 'current-warehouse-source-not-ready'; output = $warehouseSourceOutput.Trim() })
            }
        } catch {
            $errors.Add([ordered]@{ type = 'invalid-current-warehouse-source-json'; output = $warehouseSourceOutput.Trim() })
        }
    }

    $warehouseFlashOutput = & $pythonPath $warehouseSourceValidatorPath --vault-root $VaultRoot --mode flash-write 2>&1 | Out-String
    $warehouseFlashExitCode = $LASTEXITCODE
    try {
        $warehouseFlashGateResult = $warehouseFlashOutput | ConvertFrom-Json
        $derivedStatus = [string]$warehouseFlashGateResult.derivedStatus
        if ($derivedStatus -eq 'needs_rebuild_for_current_source') {
            if ($warehouseFlashExitCode -ne 2 -or [bool]$warehouseFlashGateResult.allowed -or [string]$warehouseFlashGateResult.nextAction -ne 'stop_stale_unified_price_rebuild_required') {
                $errors.Add([ordered]@{ type = 'stale-warehouse-price-gate-not-blocked'; output = $warehouseFlashOutput.Trim() })
            }
        } elseif ($warehouseFlashExitCode -ne 0 -or -not [bool]$warehouseFlashGateResult.allowed) {
            $errors.Add([ordered]@{ type = 'current-warehouse-price-gate-failed'; output = $warehouseFlashOutput.Trim() })
        }
    } catch {
        $errors.Add([ordered]@{ type = 'invalid-warehouse-flash-gate-json'; output = $warehouseFlashOutput.Trim() })
    }

    $selectionEvidenceOutput = & $pythonPath $selectionEvidenceTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'selection-evidence-tests-failed'; output = $selectionEvidenceOutput.Trim() })
    } else {
        $selectionEvidenceTestResult = $selectionEvidenceOutput.Trim()
    }

    $linkDispositionOutput = & $pythonPath $linkDispositionTestPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'listing-link-disposition-tests-failed'; output = $linkDispositionOutput.Trim() })
    } else {
        $linkDispositionTestResult = $linkDispositionOutput.Trim()
    }

    $LASTEXITCODE = 0
    $deepReasoningOutput = & $deepReasoningTestPath -VaultRoot $VaultRoot 2>&1 | Out-String
    if (-not $?) {
        $errors.Add([ordered]@{ type = 'deep-reasoning-behavior-tests-failed'; output = $deepReasoningOutput.Trim() })
    }

    $codexHome = if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
    $installedRouter = Join-Path $codexHome 'skills\tiktok-content-system\modules\pure-heygen\scripts\workspace_state.py'
    if (Test-Path -LiteralPath $installedRouter -PathType Leaf) {
        $junctionOutput = & $pythonPath $installedRouter resolve 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            $errors.Add([ordered]@{ type = 'installed-skill-root-resolution-failed'; output = $junctionOutput.Trim() })
        } else {
            try {
                $junctionResolution = $junctionOutput | ConvertFrom-Json
                if ((Resolve-Path -LiteralPath ([string]$junctionResolution.vault_root)).Path -ne $VaultRoot) {
                    $errors.Add([ordered]@{ type = 'installed-skill-resolved-wrong-vault'; value = [string]$junctionResolution.vault_root })
                }
            } catch {
                $errors.Add([ordered]@{ type = 'invalid-installed-skill-resolution-json'; output = $junctionOutput.Trim() })
            }
        }
    } else {
        $warnings.Add([ordered]@{ type = 'installed-tiktok-content-skill-not-found'; path = $installedRouter })
    }

    $recoveryOutput = & $pythonPath $routerPath recover 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errors.Add([ordered]@{ type = 'current-task-recovery-failed'; output = $recoveryOutput.Trim() })
    } else {
        try {
            $recoveryResult = $recoveryOutput | ConvertFrom-Json
            if ([string]$recoveryResult.status -eq 'recovered') {
                $allowedActions = @(
                    'blocked_external_quota',
                    'stop_missing_product',
                    'stop_missing_approved_script_or_audio',
                    'prepare_one_presenter_candidate',
                    'await_presenter_approval',
                    'generate_one_video_sample',
                    'await_batch_approval',
                    'continue_serial_batch',
                    'inspect_execution_table',
                    'await_presenter_reapproval',
                    'bind_and_verify_exact_remote_avatar',
                    'stop_approval_scope_not_exact',
                    'stop_approval_sku_mismatch',
                    'stop_approved_file_mismatch',
                    'stop_approved_file_changed',
                    'stop_remote_binding_mismatch',
                    'stop_remote_preview_mismatch',
                    'stop_cross_sku_remote_avatar_reuse',
                    'await_render_match_qc',
                    'reject_remote_input_or_render_mismatch'
                )
                if ($allowedActions -notcontains [string]$recoveryResult.plan.next_action) {
                    $errors.Add([ordered]@{ type = 'invalid-recovered-next-action'; value = [string]$recoveryResult.plan.next_action })
                }
                if ([string]$recoveryResult.task_id -eq '20260824-5sku-pure-heygen') {
                    if ([string]$recoveryResult.plan.next_action -ne 'blocked_external_quota') {
                        $errors.Add([ordered]@{ type = 'unexpected-current-next-action'; value = [string]$recoveryResult.plan.next_action })
                    }
                    if (-not [bool]$recoveryResult.plan.sample_approved) {
                        $errors.Add([ordered]@{ type = 'approved-sample-not-recovered' })
                    }
                    if (-not [bool]$recoveryResult.plan.batch_approved) {
                        $errors.Add([ordered]@{ type = 'approved-batch-standard-not-recovered' })
                    }
                    if ([string]$recoveryResult.plan.active_standard_id -ne 'STD-CNT-PURE-HEYGEN-20260827-01') {
                        $errors.Add([ordered]@{ type = 'wrong-active-batch-standard'; value = [string]$recoveryResult.plan.active_standard_id })
                    }
                }
            } else {
                $warnings.Add([ordered]@{ type = 'no-unique-current-pure-heygen-task'; status = [string]$recoveryResult.status })
            }
        } catch {
            $errors.Add([ordered]@{ type = 'invalid-recovery-json'; output = $recoveryOutput.Trim() })
        }
    }
}

if (Test-Path -LiteralPath $rulePath -PathType Leaf) {
    $rules = Get-Content -LiteralPath $rulePath -Raw -Encoding utf8
    foreach ($ruleId in @('SYS-010', 'SYS-011', 'CNT-009', 'CNT-010', 'CNT-011', 'CNT-012', 'CNT-013', 'COM-011', 'COM-013', 'IP-003', 'IP-004')) {
        if ($rules -notmatch [regex]::Escape($ruleId)) {
            $errors.Add([ordered]@{ type = 'missing-active-operational-rule'; id = $ruleId })
        }
    }
}

$result = [ordered]@{
    vaultRoot = $VaultRoot
    productionWorkRoot = $productionRoot
    checkedAt = (Get-Date).ToUniversalTime().ToString('o')
    behaviorTests = $unitTestResult
    presenterImageGateTests = $presenterImageGateTestResult
    remoteInputGateTests = $remoteInputGateTestResult
    cleanupRejectedMediaTests = $cleanupRejectedMediaTestResult
    flashPriceBehaviorTests = $flashPriceTestResult
    flashOoxmlIntegrityTests = $flashIntegrityTestResult
    warehouseSourceTests = $warehouseSourceTestResult
    warehouseSourcePath = if ($null -ne $warehouseSourceCheckResult) { [string]$warehouseSourceCheckResult.sourcePath } else { $null }
    warehouseSourceHashVerified = if ($null -ne $warehouseSourceCheckResult) { [bool]$warehouseSourceCheckResult.sourceHashVerified } else { $false }
    warehouseFlashGate = if ($null -ne $warehouseFlashGateResult) { [string]$warehouseFlashGateResult.nextAction } else { $null }
    selectionEvidenceTests = $selectionEvidenceTestResult
    listingLinkDispositionTests = $linkDispositionTestResult
    recoveredTask = if ($null -ne $recoveryResult) { [string]$recoveryResult.task_dir } else { $null }
    recoveredNextAction = if ($null -ne $recoveryResult) { [string]$recoveryResult.plan.next_action } else { $null }
    recoveredStandardId = if ($null -ne $recoveryResult) { [string]$recoveryResult.plan.active_standard_id } else { $null }
    installedSkillVaultRoot = if ($null -ne $junctionResolution) { [string]$junctionResolution.vault_root } else { $null }
    errors = @($errors)
    warnings = @($warnings)
    passed = ($errors.Count -eq 0)
}

$result | ConvertTo-Json -Depth 7

if ($errors.Count -gt 0) {
    throw 'Operational knowledge validation failed.'
}
