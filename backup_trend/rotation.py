# -*- coding: utf-8 -*-
"""Rotation des fichiers .bak du programme."""
import glob
import os

def lister_backups(cfg):
    motif = os.path.join(cfg["repertoire"], cfg["prefixe"] + "_*.bak")
    fichiers = [p for p in glob.glob(motif) if os.path.isfile(p)]
    fichiers.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return fichiers

def appliquer_rotation(cfg, logger):
    fichiers = lister_backups(cfg)
    a_supprimer = fichiers[cfg["nombre_a_conserver"]:]
    for chemin in a_supprimer:
        try:
            os.remove(chemin)
            logger.info("Rotation: suppression de %s", chemin)
        except OSError as exc:
            logger.error("Rotation: impossible de supprimer %s: %s", chemin, exc)
    logger.info("Rotation terminee: %s sauvegarde(s) conservee(s), maximum configure=%s",
                len(lister_backups(cfg)), cfg["nombre_a_conserver"])
