[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$buildRoot = $PSScriptRoot
$cacheRoot = Join-Path $buildRoot '.cache'
$runtimeRoot = Join-Path $buildRoot 'bundle\python'
New-Item -ItemType Directory -Path $cacheRoot, $runtimeRoot -Force | Out-Null
$archivePath = Join-Path $cacheRoot 'python-3.14.8-embed-amd64.zip'
$expectedHash = 'a93abe456ab01bd96d7a085b3cdb6566b3063f4241360d114142fbdb07f0a310'
if (-not (Test-Path -LiteralPath $archivePath)) {
    Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.14.8/python-3.14.8-embed-amd64.zip' -OutFile $archivePath
}
if ((Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { throw 'Python官方包SHA256校验失败，未解压。' }
Expand-Archive -LiteralPath $archivePath -DestinationPath $runtimeRoot -Force
Write-Output 'Python嵌入式运行环境已下载并通过官方SHA256核验。'
