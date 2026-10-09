# Sauvegarde SQL Server i96X — Trend 963 / chaufferie d'Allègre

**Branche de développement : installation non encore validée sur le PC de la chaufferie.**

## Fonctionnement
Le programme sauvegarde la base SQL Server `i96X` via `sqlcmd -E -b`, avec `CHECKSUM`, vérification facultative `RESTORE VERIFYONLY WITH CHECKSUM`, journalisation et rotation après succès uniquement. Il ne dépend d'aucun paquet Python externe.

## Installation depuis une copie locale du dépôt
Dans PowerShell administrateur :

```powershell
.\Installer-BackupI96X.ps1 -Python 'C:\Chemin\python.exe'
```

L'installateur prépare la tâche **désactivée** `Sauvegarde BDD Trend 963` pour le lundi à 14 h 05, sous le compte `SYSTEM`. Il conserve `backup_i96x.ini` s'il existe, ne lance aucune sauvegarde et ne supprime aucun fichier `.bak`.

**Important :** `SYSTEM` doit avoir les droits SQL appropriés ; ils ne sont pas accordés automatiquement. Le service SQL Server doit pouvoir écrire dans `C:\Backup_SQL`. La migration d'une tâche existante exige `-Update` et remplace celle-ci par une tâche désactivée : exporter d'abord sa définition et vérifier les droits avant bascule.

## Tests et exploitation

```powershell
python -m unittest discover -s tests -v
python backup_i96x.py --once --config backup_i96x.ini
Get-ScheduledTask -TaskName 'Sauvegarde BDD Trend 963'
```

Attention : `--once` effectue une véritable sauvegarde et peut déclencher la rotation. Ne lancer qu'après vérification de la configuration et des sauvegardes existantes. Une restauration sur une instance de test est recommandée.

Mise à jour depuis une nouvelle copie du dépôt :

```powershell
.\Maj-BackupI96X.ps1 -Python 'C:\Chemin\python.exe'
```

## Limites actuelles
Cette première version ne contient pas encore de téléchargement automatique des releases GitHub, de notification par e-mail ou de contrôle préventif de l'espace disque. Les sauvegardes doivent aussi être copiées hors du disque local.
