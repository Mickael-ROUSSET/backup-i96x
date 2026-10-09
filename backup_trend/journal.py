# -*- coding: utf-8 -*-
"""Journal fichier et console."""
import logging
import os

def initialiser_logger(chemin, niveau="INFO"):
    dossier = os.path.dirname(chemin)
    if dossier and not os.path.isdir(dossier):
        os.makedirs(dossier)
    logger = logging.getLogger("backup_i96x")
    logger.setLevel(getattr(logging, niveau, logging.INFO))
    logger.handlers = []
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh = logging.FileHandler(chemin, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger
