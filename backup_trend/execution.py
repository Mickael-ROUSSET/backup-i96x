# -*- coding: utf-8 -*-
"""Orchestration d'un cycle complet de sauvegarde."""
from .sql_backup import creer_backup, verifier_backup
from .rotation import appliquer_rotation

def executer_cycle(cfg, logger):
    chemin = creer_backup(cfg, logger)
    if cfg["verification"]:
        verifier_backup(cfg, chemin, logger)
    appliquer_rotation(cfg, logger)
    return chemin
