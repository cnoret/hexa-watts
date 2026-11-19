"""
Construction des variables d'entrée du modèle de prédiction.

Ce module est partagé par le script d'entraînement (scripts/entrainer_modele.py)
et par la page Modélisation : les deux construisent ainsi exactement les mêmes
variables, dans le même ordre.
"""

import datetime

import numpy as np
import pandas as pd

REGIONS = [
    "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne",
    "Centre-Val de Loire", "Grand Est", "Hauts-de-France", "Île-de-France",
    "Normandie", "Nouvelle-Aquitaine", "Occitanie", "Pays de la Loire",
    "Provence-Alpes-Côte d'Azur",
]

# Ordre des colonnes attendu par le modèle
COLONNES = [
    "Région",
    "TMin (°C)",
    "TMoy (°C)",
    "TMax (°C)",
    "Heure",
    "Jour_semaine",
    "Ferie",
    "sin_jour_annee",
    "cos_jour_annee",
    "Année",
]


def _paques(annee):
    """Date du dimanche de Pâques (algorithme de Meeus pour le calendrier grégorien)."""
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = (h + l - 7 * m + 114) % 31 + 1
    return datetime.date(annee, mois, jour)


def jours_feries(annee):
    """Ensemble des jours fériés nationaux en France métropolitaine."""
    paques = _paques(annee)
    fixes = [(1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25)]
    mobiles = [paques + datetime.timedelta(days=n) for n in (1, 39, 50)]
    return {datetime.date(annee, m, j) for m, j in fixes} | set(mobiles)


def construire_caracteristiques(region, dates, heures, tmin, tmoy, tmax):
    """
    Assemble le tableau de variables attendu par le modèle.

    Args:
        region: nom de région (ou série de noms).
        dates: série de dates (datetime64) ou date unique.
        heures: heure décimale entre 0 et 24 (23.5 pour 23 h 30).
        tmin, tmoy, tmax: températures journalières en °C.

    Returns:
        pd.DataFrame: une ligne par observation, colonnes dans l'ordre COLONNES.
    """
    dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    n = len(dates)

    def colonne(valeur):
        if np.ndim(valeur) == 0:
            return np.full(n, valeur)
        return np.asarray(valeur)

    annees = dates.dt.year
    feries = set()
    for annee in annees.unique():
        feries |= jours_feries(int(annee))

    # Jour de l'année ramené sur un cercle : le 31 décembre est voisin du 1er janvier
    jour_annee = dates.dt.dayofyear.to_numpy()
    angle = 2 * np.pi * (jour_annee - 1) / 365.25

    return pd.DataFrame(
        {
            "Région": colonne(region),
            "TMin (°C)": colonne(tmin).astype(float),
            "TMoy (°C)": colonne(tmoy).astype(float),
            "TMax (°C)": colonne(tmax).astype(float),
            "Heure": colonne(heures).astype(float),
            "Jour_semaine": dates.dt.dayofweek.to_numpy(),
            "Ferie": dates.dt.date.isin(feries).to_numpy().astype(int),
            "sin_jour_annee": np.sin(angle),
            "cos_jour_annee": np.cos(angle),
            "Année": annees.to_numpy(),
        },
        columns=COLONNES,
    )
