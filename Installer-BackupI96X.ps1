#requires -Version 5.1
<#
.SYNOPSIS
  Installe les sources locales du depot et prepare une tache hebdomadaire desactivee.
.DESCRIPTION
  Executez ce script depuis une copie de travail ou archive du depot.
  Aucune sauvegarde n'est lancee pendant l'installation.
  La tache est volontairement DESACTIVEE jusqu'a validation des droits SQL.
#>
param(
    [string]$InstallDir = 'C:\Users\Public\SupervisionMairie\SauvegardeBase\backup_i96x',
    [string]$TaskName = 'Sauvegarde BDD Trend 963',
    [string]$Python = '',
    [switch]$Update
)
$ErrorActionPreference = 'Stop'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Ouvrez PowerShell en tant qu administrateur.'
}
$InstallDir = [IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
if ($InstallDir.StartsWith('\\') -or $InstallDir -eq [IO.Path]::GetPathRoot($InstallDir).TrimEnd('\')) {
    throw 'Le dossier installation doit etre un sous-dossier local.'
}
$source = $PSScriptRoot
if ($source.TrimEnd('\') -eq $InstallDir) { throw 'Executez depuis le depot, hors du dossier de destination.' }
$required = @('backup_i96x.py','backup_i96x.ini.example','backup_trend\__init__.py','backup_trend\configuration.py','backup_trend\execution.py','backup_trend\journal.py','backup_trend\rotation.py','backup_trend\sql_backup.py')
foreach ($file in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $source $file) -PathType Leaf)) { throw "Fichier manquant : $file" }
}
if (-not $Python) {
    $cmd = Get-Command python.exe -CommandType Application -ErrorAction SilentlyContinue
    if ($cmd) { $Python = $cmd.Source }
}
if (-not $Python -or -not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Python introuvable. Fournissez -Python avec le chemin complet.' }
& $Python -c 'import sys; assert sys.version_info >= (3, 9)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.9 minimum requis pour cette installation.' }
$oldTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($oldTask -and -not $Update) {
    throw "La tache existe deja : $TaskName. Aucune modification. Utilisez -Update apres sauvegarde de la definition existante."
}
if ($oldTask -and $oldTask.State -eq 'Running') { throw 'Tache en cours : attendre sa fin avant mise a jour.' }
if ($Update -and -not (Test-Path -LiteralPath (Join-Path $InstallDir 'backup_i96x.py'))) { throw 'Installation existante introuvable.' }
$oldXml = if ($oldTask) { Export-ScheduledTask -TaskName $TaskName } else { $null }
$backup = Join-Path $env:TEMP ('backup-i96x-rollback-' + [guid]::NewGuid().ToString('N'))
$hadInstall = Test-Path -LiteralPath $InstallDir
$taskChanged = $false
try {
    if ($hadInstall) { Copy-Item -LiteralPath $InstallDir -Destination $backup -Recurse -Force }
    New-Item -ItemType Directory -Path (Join-Path $InstallDir 'backup_trend') -Force | Out-Null
    foreach ($file in $required) {
        $target = Join-Path $InstallDir $file
        Copy-Item -LiteralPath (Join-Path $source $file) -Destination $target -Force
    }
    $ini = Join-Path $InstallDir 'backup_i96x.ini'
    if (-not (Test-Path -LiteralPath $ini)) {
        Copy-Item -LiteralPath (Join-Path $source 'backup_i96x.ini.example') -Destination $ini
    }
    & $Python -m compileall -q (Join-Path $InstallDir 'backup_i96x.py') (Join-Path $InstallDir 'backup_trend')
    if ($LASTEXITCODE -ne 0) { throw 'Compilation Python echouee.' }
    $action = New-ScheduledTaskAction -Execute $Python -Argument ('"' + (Join-Path $InstallDir 'backup_i96x.py') + '" --once --config "' + $ini + '"') -WorkingDirectory $InstallDir
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At '20:00'
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 4) -MultipleInstances IgnoreNew
    # SYSTEM n'a pas automatiquement les droits SQL. Ne jamais activer avant verification.
    $account = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    $taskChanged = $true
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $account -Force | Out-Null
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Host 'Installation preparee. Tache DESACTIVEE : validez les droits SQL du compte SYSTEM avant activation.'
    Write-Host "Configuration conservee : $ini"
    Write-Host "Copie de securite eventuelle : $backup"
} catch {
    $errorOriginal = $_
    if ($taskChanged) {
        if ($oldXml) { Register-ScheduledTask -TaskName $TaskName -Xml $oldXml -Force | Out-Null }
        else { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue }
    }
    if ($hadInstall -and (Test-Path -LiteralPath $backup)) {
        Remove-Item -LiteralPath $InstallDir -Recurse -Force
        Copy-Item -LiteralPath $backup -Destination $InstallDir -Recurse
    } elseif (-not $hadInstall -and (Test-Path -LiteralPath $InstallDir)) {
        Remove-Item -LiteralPath $InstallDir -Recurse -Force
    }
    throw $errorOriginal
}
