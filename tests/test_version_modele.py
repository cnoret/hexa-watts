"""
Le modèle enregistré correspond à la version de scikit-learn installée.

scikit-learn ne garantit pas qu'un modèle enregistré avec une version se
recharge à l'identique avec une autre. Si une mise à jour de scikit-learn
(par exemple une PR Dependabot) arrive sans que le modèle soit réentraîné,
ces tests échouent et indiquent la marche à suivre.
"""

import json
import warnings

import joblib
import sklearn
from sklearn.exceptions import InconsistentVersionWarning

from content.modelisation import CHEMIN_METRIQUES, CHEMIN_MODELE
from tests.conftest import RACINE
from tests.test_dependances import epinglages

A_FAIRE = (
    "Réentraîner le modèle avec `python scripts/entrainer_modele.py`, "
    "puis commiter models/modele_consommation.joblib et models/metriques.json."
)


def version_du_modele():
    metriques = json.loads((RACINE / CHEMIN_METRIQUES).read_text(encoding="utf-8"))
    return metriques["scikit_learn"]


def test_metriques_et_scikit_learn_installe_ont_la_meme_version():
    attendue = version_du_modele()
    assert sklearn.__version__ == attendue, (
        f"Le modèle a été entraîné avec scikit-learn {attendue}, "
        f"mais la version installée est {sklearn.__version__}. {A_FAIRE}"
    )


def test_metriques_et_requirements_ont_la_meme_version():
    attendue = version_du_modele()
    epinglee = epinglages()["scikit-learn"]
    assert epinglee == attendue, (
        f"requirements.txt demande scikit-learn {epinglee}, "
        f"mais le modèle a été entraîné avec la {attendue}. {A_FAIRE}"
    )


def test_modele_se_charge_sans_avertissement_de_version():
    """Vérifie le fichier .joblib lui-même, au cas où metriques.json serait resté ancien."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        try:
            joblib.load(RACINE / CHEMIN_MODELE)
        except InconsistentVersionWarning as avertissement:
            raise AssertionError(f"{avertissement} {A_FAIRE}") from None
