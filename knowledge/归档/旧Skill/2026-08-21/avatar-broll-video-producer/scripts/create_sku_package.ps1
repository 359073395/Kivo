param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$Sku,

    [Parameter(Mandatory = $true)]
    [string]$ScriptId,

    [string]$Date = (Get-Date -Format 'yyyyMMdd')
)

$ErrorActionPreference = 'Stop'

function ConvertTo-SafeName {
    param([Parameter(Mandatory = $true)][string]$Value)

    $safe = $Value.Trim()
    foreach ($char in [System.IO.Path]::GetInvalidFileNameChars()) {
        $safe = $safe.Replace([string]$char, '_')
    }
    $safe = $safe -replace '\s+', '_'
    $safe = $safe.TrimEnd('.', ' ')
    if ([string]::IsNullOrWhiteSpace($safe)) {
        throw 'A safe folder name could not be derived from the supplied value.'
    }
    return $safe
}

$safeSku = ConvertTo-SafeName -Value $Sku
$safeScriptId = ConvertTo-SafeName -Value $ScriptId
$runRoot = Join-Path (Join-Path $OutputRoot $safeSku) ("{0}_{1}" -f $safeScriptId, $Date)

$relativeFolders = @(
    '00_task',
    '01_product_white',
    '02_presenter_gpt',
    '03_audio_user',
    '04_lipsync_heygen',
    '05_broll',
    '05_broll\pain',
    '05_broll\product',
    '05_broll\usage',
    '05_broll\proof',
    '05_broll\lifestyle',
    '06_excel',
    '07_chatcut',
    '08_output',
    '08_output\draft',
    '08_output\final',
    'logs'
)

[System.IO.Directory]::CreateDirectory($runRoot) | Out-Null
foreach ($relativeFolder in $relativeFolders) {
    [System.IO.Directory]::CreateDirectory((Join-Path $runRoot $relativeFolder)) | Out-Null
}

$manifest = [ordered]@{
    schema_version = 1
    sku = $Sku
    safe_sku = $safeSku
    script_id = $ScriptId
    safe_script_id = $safeScriptId
    created_at = (Get-Date).ToString('o')
    run_root = $runRoot
    status = 'preflight_ready'
    required_inputs = [ordered]@{
        product_white = [ordered]@{
            folder = (Join-Path $runRoot '01_product_white')
            status = 'pending'
        }
        final_user_audio = [ordered]@{
            folder = (Join-Path $runRoot '03_audio_user')
            status = 'pending'
        }
        user_broll = [ordered]@{
            folder = (Join-Path $runRoot '05_broll')
            status = 'pending'
        }
    }
    generated_outputs = [ordered]@{
        presenter_image = (Join-Path $runRoot '02_presenter_gpt')
        heygen_lipsync = (Join-Path $runRoot '04_lipsync_heygen')
        excel_plan = (Join-Path $runRoot '06_excel')
        chatcut_project = (Join-Path $runRoot '07_chatcut')
        draft_video = (Join-Path $runRoot '08_output\draft')
        final_video = (Join-Path $runRoot '08_output\final')
    }
}

$manifestPath = Join-Path $runRoot '00_task\package_manifest.json'
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

$activeTask = [ordered]@{
    task_id = "{0}_{1}_{2}" -f $safeSku, $safeScriptId, $Date
    sku = $Sku
    script_id = $ScriptId
    run_root = $runRoot
    status = 'preflight_ready'
    updated_at = (Get-Date).ToString('o')
}
$activeTask | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runRoot 'ACTIVE_TASK.json') -Encoding UTF8

Write-Output $runRoot
