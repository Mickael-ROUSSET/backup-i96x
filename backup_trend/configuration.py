# -*- coding: utf-8 -*-
"""Chargement et validation de la configuration INI."""
import configparser
import os

class ConfigurationError(Exception):
    pass

def _get_bool(section, key, default):
    if key not in section:
        return default
    try:
        return section.getboolean(key)
    except ValueError:
        raise ConfigurationError("Valeur booleenne invalide pour %s" % key)

def charger_configuration(chemin):
    if not os.path.isfile(chemin):
        raise ConfigurationError("Fichier de configuration introuvable: %s" % chemin)
    parser = configparser.ConfigParser()
    parser.read(chemin, encoding="utf-8")
    if "sql" not in parser or "sauvegarde" not in parser:
        raise ConfigurationError("Sections [sql] et [sauvegarde] obligatoires")
    sql = parser["sql"]
    sauvegarde = parser["sauvegarde"]
    journal = parser["journal"] if "journal" in parser else {}
    cfg = {
        "serveur": sql.get("serveur", "localhost").strip(),
        "base": sql.get("base", "i96X").strip(),
        "sqlcmd": sql.get("sqlcmd", "sqlcmd").strip(),
        "auth_windows": _get_bool(sql, "authentification_windows", True),
        "repertoire": os.path.abspath(os.path.expandvars(sauvegarde.get("repertoire", r"C:\Backup_SQL"))),
        "frequence_minutes": sauvegarde.getint("frequence_minutes", 1440),
        "nombre_a_conserver": sauvegarde.getint("nombre_a_conserver", 14),
        "verification": _get_bool(sauvegarde, "verification_restore_verifyonly", True),
        "prefixe": sauvegarde.get("prefixe", "i96X").strip(),
        "log_file": os.path.abspath(os.path.expandvars(journal.get("fichier", r"C:\Backup_SQL\backup_i96X.log"))) if journal else r"C:\Backup_SQL\backup_i96X.log",
        "niveau_log": journal.get("niveau", "INFO").strip().upper() if journal else "INFO",
    }
    if not cfg["auth_windows"]:
        raise ConfigurationError("Cette version prend uniquement en charge l'authentification Windows")
    if not cfg["serveur"] or not cfg["base"]:
        raise ConfigurationError("Serveur et base SQL obligatoires")
    if cfg["frequence_minutes"] <= 0 or cfg["nombre_a_conserver"] < 1:
        raise ConfigurationError("Frequence et retention doivent etre positives")
    return cfg
