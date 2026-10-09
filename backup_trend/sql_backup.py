# -*- coding: utf-8 -*-
"""Execution du BACKUP DATABASE et de sa verification via sqlcmd."""
import os
import subprocess
from datetime import datetime

class BackupError(Exception):
    pass

def _echapper_sql_literal(texte):
    return texte.replace("'", "''")

def _echapper_identifiant_sql(texte):
    return texte.replace("]", "]]")

def _commande_sqlcmd(cfg, requete):
    cmd = [cfg["sqlcmd"], "-S", cfg["serveur"]]
    if cfg["auth_windows"]:
        cmd.append("-E")
    cmd.extend(["-b", "-Q", requete])
    return cmd

def executer_sql(cfg, requete, logger):
    cmd = _commande_sqlcmd(cfg, requete)
    logger.debug("Execution sqlcmd: %s", " ".join(cmd[:-1]) + " <requete SQL>")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        sortie, _ = proc.communicate()
    except OSError as exc:
        raise BackupError("Impossible de lancer sqlcmd: %s" % exc)
    if sortie:
        for ligne in sortie.splitlines():
            logger.info("sqlcmd | %s", ligne)
    if proc.returncode != 0:
        raise BackupError("sqlcmd a retourne le code %s" % proc.returncode)
    return sortie

def construire_chemin_backup(cfg, maintenant=None):
    maintenant = maintenant or datetime.now()
    nom = "%s_%s.bak" % (cfg["prefixe"], maintenant.strftime("%Y-%m-%d_%H-%M-%S"))
    return os.path.join(cfg["repertoire"], nom)

def creer_backup(cfg, logger):
    if not os.path.isdir(cfg["repertoire"]):
        os.makedirs(cfg["repertoire"])
    chemin = construire_chemin_backup(cfg)
    base = _echapper_identifiant_sql(cfg["base"])
    fichier = _echapper_sql_literal(chemin)
    requete = "BACKUP DATABASE [%s] TO DISK=N'%s' WITH INIT, CHECKSUM, STATS=10;" % (base, fichier)
    logger.info("Debut sauvegarde de la base %s vers %s", cfg["base"], chemin)
    executer_sql(cfg, requete, logger)
    if not os.path.isfile(chemin):
        raise BackupError("SQL Server annonce la fin du backup mais le fichier est introuvable: %s" % chemin)
    if os.path.getsize(chemin) == 0:
        raise BackupError("Le fichier de sauvegarde est vide: %s" % chemin)
    logger.info("Sauvegarde creee: %s (%.1f Mo)", chemin, os.path.getsize(chemin) / 1048576.0)
    return chemin

def verifier_backup(cfg, chemin, logger):
    fichier = _echapper_sql_literal(chemin)
    requete = "RESTORE VERIFYONLY FROM DISK=N'%s' WITH CHECKSUM;" % fichier
    logger.info("Verification RESTORE VERIFYONLY de %s", chemin)
    executer_sql(cfg, requete, logger)
    logger.info("Verification terminee avec succes")
