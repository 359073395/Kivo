$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $skillRoot 'references\source-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$productSourceRelative = Join-Path 'references' ([string]$manifest.product_knowledge.file).Replace('/', '\')
$operationsSourceRelative = Join-Path 'references' ([string]$manifest.operations_knowledge.file).Replace('/', '\')

$required = @(
  'SKILL.md',
  'agents\openai.yaml',
  'agents\generic-system-prompt.md',
  'references\knowledge-index.md',
  'references\source-manifest.json',
  $productSourceRelative,
  'references\product\product_catalog.jsonl',
  $operationsSourceRelative,
  'references\operations\tiktok-operations-extracted.md',
  'references\operations\operations_extraction_summary.json',
  'references\selection\selection-logic.md',
  'references\benchmark\benchmark-research.md',
  'references\copywriting\rewrite-playbook.md',
  'references\fixtures\rewrite-regression-fixture.json',
  'references\policy-and-rights.md',
  'references\output-contract.md',
  'references\test-cases.md'
)

$missing = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $skillRoot $_) -PathType Leaf) })
if ($missing.Count) { throw "Missing required files: $($missing -join ', ')" }

$catalogPath = Join-Path $skillRoot 'references\product\product_catalog.jsonl'
$rows = @(Get-Content -LiteralPath $catalogPath -Encoding UTF8 | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
if ($rows.Count -ne 571) { throw "Expected 571 product rows, got $($rows.Count)" }
$uniqueSkus = @($rows | Group-Object sku)
if ($uniqueSkus.Count -ne 571 -or @($uniqueSkus | Where-Object Count -ne 1).Count) { throw 'SKU mappings are not unique' }

$descriptive = @('specification','ingredients','selling_points','usage','audience','attributes_certifications')
foreach ($row in $rows) {
  if (-not $row.sku -or -not $row.source_row -or -not $row.image_thumbnail) { throw "Missing required product key for SKU $($row.sku)" }
  foreach ($field in $descriptive) {
    if ([string]$row.$field -eq '37') { throw "Placeholder 37 remains in $field for SKU $($row.sku)" }
  }
  if ($row.PSObject.Properties.Name -contains 'local_original_image_path') { throw "Absolute original path leaked for SKU $($row.sku)" }
  if ([System.IO.Path]::IsPathRooted([string]$row.image_thumbnail)) { throw "Thumbnail path is not portable for SKU $($row.sku)" }
  $mappedImage = Join-Path $skillRoot ([string]$row.image_thumbnail).Replace('/', '\')
  if (-not (Test-Path -LiteralPath $mappedImage -PathType Leaf)) { throw "Missing thumbnail for SKU $($row.sku)" }
}

$thumbDir = Join-Path $skillRoot 'assets\product-thumbnails'
$thumbs = @(Get-ChildItem -LiteralPath $thumbDir -File)
if ($thumbs.Count -ne 571) { throw "Expected 571 thumbnails, got $($thumbs.Count)" }
$mappedNames = @($rows | ForEach-Object { Split-Path ([string]$_.image_thumbnail) -Leaf } | Sort-Object -Unique)
$actualNames = @($thumbs.Name | Sort-Object -Unique)
if (Compare-Object $mappedNames $actualNames) { throw 'Thumbnail references and files are not one-to-one' }
foreach ($thumb in $thumbs) {
  if ($thumb.Length -le 0) { throw "Empty thumbnail: $($thumb.Name)" }
  $stream = [System.IO.File]::OpenRead($thumb.FullName)
  try {
    $bytes = New-Object byte[] 8
    [void]$stream.Read($bytes, 0, 8)
  } finally { $stream.Dispose() }
  $isJpeg = $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xD8
  $isPng = $bytes[0] -eq 0x89 -and $bytes[1] -eq 0x50 -and $bytes[2] -eq 0x4E -and $bytes[3] -eq 0x47
  if (-not ($isJpeg -or $isPng)) { throw "Unsupported/bad image signature: $($thumb.Name)" }
}

$qinfeiyan = @($rows | Where-Object sku -eq 'Qinfeiyan Shampoo')
if ($qinfeiyan.Count -ne 1) { throw 'Qinfeiyan Shampoo exact-match regression failed' }
$q = $qinfeiyan[0]
if ($null -ne $q.ingredients -or $null -ne $q.usage) { throw 'Qinfeiyan missing-field normalization failed' }
if ([double]$q.listing_original_price_idr -ne 96760 -or [double]$q.daily_price_idr -ne 48380 -or [double]$q.activity_price_idr -ne 45380) { throw 'Qinfeiyan price regression failed' }
if (-not (@($q.claim_risk_tags) -contains 'hair_growth_or_loss')) { throw 'Qinfeiyan claim risk regression failed' }

if ([int]$manifest.product_knowledge.sku_count -ne 571) { throw 'Manifest SKU count is invalid' }
$hashChecks = @(
  @($productSourceRelative, [string]$manifest.product_knowledge.sha256),
  @($operationsSourceRelative, [string]$manifest.operations_knowledge.sha256)
)
foreach ($check in $hashChecks) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $skillRoot $check[0])).Hash
  if ($actual -ne $check[1]) { throw "Source hash mismatch: $($check[0])" }
}

$skillText = Get-Content -LiteralPath (Join-Path $skillRoot 'SKILL.md') -Raw -Encoding UTF8
$linkMatches = [regex]::Matches($skillText, '\]\(([^)]+)\)')
foreach ($match in $linkMatches) {
  $target = $match.Groups[1].Value
  if (-not (Test-Path -LiteralPath (Join-Path $skillRoot $target))) { throw "Broken SKILL.md link: $target" }
}

Write-Output 'Portable bundle validation passed'
Write-Output "SKUs: $($rows.Count)"
Write-Output "Thumbnails: $($thumbs.Count)"
Write-Output "Required files: $($required.Count)"
