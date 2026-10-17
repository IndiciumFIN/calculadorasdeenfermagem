# Recupera o ZIP integral do Atlas a partir das partes imutáveis no Google Drive.
# PowerShell 5+/Windows, sem instalar módulos nem acessar rede.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$man = Get-Content -LiteralPath (Join-Path $root 'MANIFESTO_DRIVE_PARTES_SHA256.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$dest = Join-Path $root $man.original_name
if(Test-Path -LiteralPath $dest){
  $old = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
  if($old -eq $man.original_sha256){Write-Host 'ZIP ja existe e SHA-256 foi confirmado.'; exit 0}
  throw 'Arquivo existente tem hash incorreto. Nao sobrescrever; mover a copia invalida para outra pasta manualmente.'
}
$temporary = "$dest.incompleto"
if(Test-Path -LiteralPath $temporary){throw 'Reconstrucao incompleta existente: verifique/remova manualmente antes de continuar.'}
$target = [System.IO.File]::Open($temporary,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
try {
  foreach($p in $man.parts_detail){
    $file = Join-Path $root $p.name
    if(!(Test-Path -LiteralPath $file)){throw "Parte ausente: $($p.name)"}
    $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if($actual -ne $p.sha256){throw "SHA-256 invalido: $($p.name)"}
    $source = [System.IO.File]::OpenRead($file)
    try {$source.CopyTo($target)} finally {$source.Dispose()}
    Write-Host "Validado $($p.index)/$($man.parts) : $($p.name)"
  }
} finally {$target.Dispose()}
$gotLength=(Get-Item -LiteralPath $temporary).Length
if($gotLength -ne $man.original_bytes){throw "Comprimento diferente: $gotLength / $($man.original_bytes)"}
$gotHash = (Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant()
if($gotHash -ne $man.original_sha256){throw 'HASH INTEGRAL INVALIDO - NAO USAR O ARQUIVO' }
Move-Item -LiteralPath $temporary -Destination $dest
Write-Host "INTEGRIDADE OK. ZIP reconstruido: $dest"
