[CmdletBinding()]
param([string]$CacheRoot = (Join-Path $PSScriptRoot '.cache'))

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$toolsRoot = Join-Path $PSScriptRoot 'bundle\python\Tools'
New-Item -ItemType Directory -Path $CacheRoot, $toolsRoot -Force | Out-Null

function Get-VerifiedArchive([string]$Name, [string]$Url, [string]$Hash) {
    $archive = Join-Path $CacheRoot $Name
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri $Url -OutFile $archive
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Hash) {
        throw "Archive checksum mismatch: $Name"
    }
    return $archive
}

$nodeArchive = Get-VerifiedArchive 'node-v24.14.1-win-x64.zip' 'https://nodejs.org/dist/v24.14.1/node-v24.14.1-win-x64.zip' '6e50ce5498c0cebc20fd39ab3ff5df836ed2f8a31aa093cecad8497cff126d70'
$nodeExtract = Join-Path $CacheRoot 'node-runtime'
Expand-Archive -LiteralPath $nodeArchive -DestinationPath $nodeExtract -Force
$nodeSource = Join-Path $nodeExtract 'node-v24.14.1-win-x64'
$nodeTarget = Join-Path $toolsRoot 'node'
New-Item -ItemType Directory -Path $nodeTarget -Force | Out-Null
Get-ChildItem -LiteralPath $nodeSource | Copy-Item -Destination $nodeTarget -Recurse -Force

$ffmpegArchive = Get-VerifiedArchive 'ffmpeg-full.7z' 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z' 'f0e46253c70dfe902bac915dfb4224f0cf1b7c6eeab9da2ccc9a5581f9a71b13'
$extractor = Join-Path $PSScriptRoot 'node_modules\electron-winstaller\vendor\7z.exe'
if (-not (Test-Path -LiteralPath $extractor)) {
    throw 'Install the desktop npm dependencies before preparing media runtimes.'
}
$ffmpegExtract = Join-Path $CacheRoot 'ffmpeg-runtime'
& $extractor x $ffmpegArchive "-o$ffmpegExtract" -y | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'FFmpeg extraction failed.' }
$ffmpegSource = Join-Path $ffmpegExtract 'ffmpeg-9.0.2-full_build'
$ffmpegTarget = Join-Path $toolsRoot 'ffmpeg'
New-Item -ItemType Directory -Path $ffmpegTarget -Force | Out-Null
foreach ($file in @('ffmpeg.exe', 'ffprobe.exe')) {
    Copy-Item -LiteralPath (Join-Path $ffmpegSource "bin\$file") -Destination $ffmpegTarget -Force
}
foreach ($file in @('LICENSE', 'README.txt')) {
    Copy-Item -LiteralPath (Join-Path $ffmpegSource $file) -Destination $ffmpegTarget -Force
}

$previousPath = $env:PATH
$env:PATH = "$nodeTarget;$previousPath"
Push-Location (Join-Path $projectRoot 'skills\builtin\video-production\vendor\video-pipeline-sdk\deps\remotion')
try {
    & (Join-Path $nodeTarget 'npm.cmd') ci
    if ($LASTEXITCODE -ne 0) { throw 'Remotion dependency installation failed.' }
    & (Join-Path $nodeTarget 'npx.cmd') --no-install remotion browser ensure
    if ($LASTEXITCODE -ne 0) { throw 'Remotion browser installation failed.' }
} finally {
    Pop-Location
    $env:PATH = $previousPath
}
Write-Output 'Verified Node.js, FFmpeg, Remotion and its rendering browser are ready.'
