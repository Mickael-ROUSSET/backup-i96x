#requires -Version 5.1
<#
.SYNOPSIS
  Telecharge et installe backup-i96x depuis le depot public GitHub.
.DESCRIPTION
  A utiliser depuis PowerShell administrateur. Ne modifie pas une tache existante.
  Le programme est installe depuis la branche de travail tant que la PR n'est pas fusionnee.
#>
$ErrorActionPreference = 'Stop'
$repo = 'Mickael-ROUSSET/backup-i96x'
$ref = 'feature/installation-backup-i96x'
$root = Join-Path $env:TEMP ('backup-i96x-install-' + [guid]::NewGuid().ToString('N'))
$zip = "$root.zip"
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $url = "https://api.github.com/repos/$repo/zipball/$ref"
    Write-Host "Telechargement de $repo ($ref)..."
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip -Headers @{'User-Agent'='backup-i96x-installer'} -TimeoutSec 120
    Expand-Archive -LiteralPath $zip -DestinationPath $root -ErrorAction Stop
    $candidates = @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter 'Installer-BackupI96X.ps1')
    if ($candidates.Count -ne 1) { throw "Archive inattendue : $($candidates.Count) installateurs trouves." }
    $installer = $candidates[0].FullName
    Write-Host 'Execution de l installateur local...'
    & $installer
    if (-not $?) { throw 'Installateur en echec.' }
} finally {
    if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
