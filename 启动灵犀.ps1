[CmdletBinding()]
param([int]$Port = 7860, [switch]$Foreground, [switch]$SkipSync)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw '本项目缺少Python环境，请先安装项目依赖。' }
$vaultRoot = if ($env:LINGXI_KNOWLEDGE_ROOT) { $env:LINGXI_KNOWLEDGE_ROOT } elseif (Test-Path -LiteralPath 'F:\Knowledge\knowledge-base.json') { 'F:\Knowledge' } else { Join-Path $projectRoot 'knowledge' }
$configPath = Join-Path $vaultRoot '辅助\配置\machine-paths.local.json'
$config = if (Test-Path -LiteralPath $configPath) { Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
$runtimeRoot = if ($env:LINGXI_DATA_ROOT) { $env:LINGXI_DATA_ROOT } elseif ($config -and $config.productionWorkRoot) { Join-Path $config.productionWorkRoot 'lingxi-platform' } else { Join-Path $env:LOCALAPPDATA 'Kivo\knowledge' }
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$env:LINGXI_KNOWLEDGE_ROOT = $vaultRoot
$env:LINGXI_DATA_ROOT = $runtimeRoot
$env:EASEL_PORT = [string]$Port
$env:PYTHONUTF8 = '1'
Push-Location $projectRoot
try {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "端口$Port已有服务，请打开 http://127.0.0.1:$Port/ 核对，或使用 -Port 指定其他端口。"
        return
    }
    if (-not $SkipSync) {
        & $pythonPath -m lingxi.knowledge build
        if ($LASTEXITCODE -ne 0) { throw '知识库整理失败，未启动网页。' }
    }
    if ($Foreground) {
        & $pythonPath -m uvicorn web.app:app --host 127.0.0.1 --port $Port
    } else {
        $proc = Start-Process -FilePath $pythonPath -ArgumentList @('-m','uvicorn','web.app:app','--host','127.0.0.1','--port',"$Port") -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeRoot 'web.stdout.log') -RedirectStandardError (Join-Path $runtimeRoot 'web.stderr.log') -PassThru
        Write-Host "Kivo 创作工作台已启动，进程 $($proc.Id)，地址 http://127.0.0.1:$Port/"
    }
} finally { Pop-Location }
