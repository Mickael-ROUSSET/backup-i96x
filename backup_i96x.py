# -*- coding: utf-8 -*-
"""Sauvegarde automatique de la base SQL Server i96X de Trend 963."""
from __future__ import print_function
import argparse
import os
import sys
import time
from backup_trend.configuration import charger_configuration, ConfigurationError
from backup_trend.journal import initialiser_logger
from backup_trend.execution import executer_cycle
from backup_trend.sql_backup import BackupError

def parser_arguments():
    parser = argparse.ArgumentParser(description="Sauvegarde automatique SQL Server i96X")
    parser.add_argument("-c", "--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_i96x.ini"), help="Chemin du fichier INI")
    parser.add_argument("--once", action="store_true", help="Effectue une seule sauvegarde puis quitte")
    return parser.parse_args()

def main():
    args = parser_arguments()
    config_path = os.path.abspath(args.config)
    try:
        cfg = charger_configuration(config_path)
        logger = initialiser_logger(cfg["log_file"], cfg["niveau_log"])
    except (ConfigurationError, OSError) as exc:
        print("ERREUR CONFIGURATION: %s" % exc, file=sys.stderr)
        return 2
    logger.info("Demarrage backup_i96x - config=%s", config_path)
    logger.info("Base=%s serveur=%s frequence=%s min conservation=%s",
                cfg["base"], cfg["serveur"], cfg["frequence_minutes"], cfg["nombre_a_conserver"])
    while True:
        try:
            executer_cycle(cfg, logger)
        except (BackupError, OSError) as exc:
            logger.exception("Echec du cycle de sauvegarde: %s", exc)
            if args.once:
                return 1
        except Exception as exc:
            logger.exception("Erreur inattendue: %s", exc)
            if args.once:
                return 1
        if args.once:
            logger.info("Fin du mode --once")
            return 0
        logger.info("Prochaine tentative dans %s minute(s)", cfg["frequence_minutes"])
        try:
            time.sleep(cfg["frequence_minutes"] * 60)
        except KeyboardInterrupt:
            logger.info("Arret demande par l'utilisateur")
            return 0

if __name__ == "__main__":
    sys.exit(main())
