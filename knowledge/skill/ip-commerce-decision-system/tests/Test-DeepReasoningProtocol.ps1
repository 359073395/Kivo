[CmdletBinding()]
param([string]$VaultRoot)

# Compatibility entrypoint. This test verifies structure and declared behavior
# surfaces only; it does not claim that a model semantically passed the cases.
& (Join-Path $PSScriptRoot 'Test-DeepReasoningStructure.ps1') -VaultRoot $VaultRoot
