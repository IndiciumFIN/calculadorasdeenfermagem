param(
  [Parameter(Mandatory=$true)][string]$InputRoot,
  [Parameter(Mandatory=$true)][string]$Workspace,
  [string]$Dataset = 'COFEN-LOCAL-001',
  [string]$RemoteCsv = '',
  [string]$Crosswalk = '',
  [ValidateSet('COFEN','ALL')][string]$Scope = 'COFEN',
  [int]$Limit = 0,
  [string]$CanonicalOutput = '',
  [string]$HandoffOutput = '',
  [switch]$OnlyVerify
)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python launcher py nao encontrado. Instale Python 3.10+.' }
if ($OnlyVerify) {
  & py -m ce_local.cli verify --workspace $Workspace
  if ($LASTEXITCODE -ne 0) { throw 'HOLD: verificacao falhou' }
  exit 0
}
$arguments = @('-m','ce_local.cli','pipeline','--input',$InputRoot,'--workspace',$Workspace,'--dataset',$Dataset,'--scope',$Scope)
if ($Limit -gt 0) { $arguments += @('--limit',[string]$Limit) }
if ($RemoteCsv) { $arguments += @('--remote-csv',$RemoteCsv) }
if ($Crosswalk) { $arguments += @('--crosswalk',$Crosswalk) }
if ($CanonicalOutput) { $arguments += @('--canonical-output',$CanonicalOutput) }
if ($HandoffOutput) { $arguments += @('--handoff-output',$HandoffOutput) }
& py @arguments
if ($LASTEXITCODE -ne 0) { throw 'HOLD: execucao local falhou. Veja as evidencias; originais nao foram alterados.' }
Write-Host 'Sem escrita remota. Sem publicacao. Kernel oficial ainda nao submetido.'
