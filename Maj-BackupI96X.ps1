#requires -Version 5.1
param(
    [string]$InstallDir = 'C:\Users\Public\SupervisionMairie\SauvegardeBase\backup_i96x',
    [string]$TaskName = 'Sauvegarde BDD Trend 963',
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Installer-BackupI96X.ps1') -InstallDir $InstallDir -TaskName $TaskName -Python $Python -Update
if (-not $?) { throw 'Mise a jour echouee.' }
