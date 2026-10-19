param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [string]$Language = 'auto',
    [ValidateRange(1, 64)]
    [int]$Threads = 8
)

$ErrorActionPreference = 'Stop'
$inputFile = (Resolve-Path -LiteralPath $InputPath).Path

$cursor = Get-Item -LiteralPath $PSScriptRoot
$knowledgeRoot = $null
while ($cursor) {
    if (Test-Path -LiteralPath (Join-Path $cursor.FullName 'knowledge-base.json') -PathType Leaf) {
        $knowledgeRoot = $cursor.FullName
        break
    }
    $cursor = $cursor.Parent
}
if (-not $knowledgeRoot) {
    throw 'Cannot locate the Knowledge root containing knowledge-base.json.'
}

$configPath = Join-Path $knowledgeRoot '辅助\配置\machine-paths.local.json'
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Missing machine-local configuration: $configPath"
}
$config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json

$python = [string]$config.videoTranscriptPython
$model = [string]$config.whisperModelPath
$work = [string]$config.whisperWorkDir
$ffmpeg = [string]$config.ffmpegPath
foreach ($required in @($python, $model, $work, $ffmpeg)) {
    if ([string]::IsNullOrWhiteSpace($required)) {
        throw 'videoTranscriptPython, whisperModelPath, whisperWorkDir, and ffmpegPath must be configured.'
    }
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Python runtime not found: $python" }
if (-not (Test-Path -LiteralPath $model -PathType Container)) { throw "Whisper model not found: $model" }
if (-not (Test-Path -LiteralPath $ffmpeg -PathType Leaf)) { throw "FFmpeg not found: $ffmpeg" }
New-Item -ItemType Directory -Path $work -Force | Out-Null

$env:KNOWLEDGE_ROOT = $knowledgeRoot
$env:WHISPER_MODEL = $model
$env:WHISPER_WORK_DIR = $work
$env:WHISPER_THREADS = [string]$Threads
$env:FFMPEG_PATH = $ffmpeg
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
if ([string]::IsNullOrWhiteSpace($Language) -or $Language -eq 'auto') {
    Remove-Item Env:WHISPER_LANG -ErrorAction SilentlyContinue
} else {
    $env:WHISPER_LANG = $Language
}

$transcribe = Join-Path $PSScriptRoot 'transcribe.py'
$merge = Join-Path $PSScriptRoot 'merge.py'
& $python $transcribe $inputFile
if ($LASTEXITCODE -ne 0) { throw "Transcription failed with exit code $LASTEXITCODE" }

$audioExtensions = @('.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.wav', '.wma')
$kind = if ($audioExtensions -contains [System.IO.Path]::GetExtension($inputFile).ToLowerInvariant()) { '音频' } else { '视频' }
$transcript = Join-Path $knowledgeRoot (Join-Path "资源\raw\sources\$kind" (([System.IO.Path]::GetFileNameWithoutExtension($inputFile)) + '_transcript.md'))
if (-not (Test-Path -LiteralPath $transcript -PathType Leaf)) { throw "Transcript output missing: $transcript" }

& $python $merge $transcript
if ($LASTEXITCODE -ne 0) { throw "Transcript merge failed with exit code $LASTEXITCODE" }
Get-Item -LiteralPath $transcript
