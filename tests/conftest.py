"""
Réglages communs aux tests.

Les pages ouvrent leurs fichiers avec des chemins relatifs (datasets/, images/,
models/) : les tests s'exécutent donc depuis la racine du dépôt, comme
`streamlit run streamlit_app.py`.
"""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RACINE = Path(__file__).resolve().parent.parent

# Même allocateur Arrow que l'application (voir streamlit_app.py)
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")

# Les 7 pages du menu : module de content/ et fonction qui affiche la page
PAGES = [
    "introduction",
    "exploration",
    "preparation",
    "visualisation",
    "modelisation",
    "conclusion",
    "ressources",
]

# Temps maximal d'une exécution de page (le premier chargement des données
# de la page Analyses prend quelques secondes)
DELAI = 120


@pytest.fixture(autouse=True)
def racine_du_depot(monkeypatch):
    monkeypatch.chdir(RACINE)


def page_app(nom):
    """AppTest qui affiche une seule page, comme le fait le menu de streamlit_app.py."""
    return AppTest.from_string(
        f"from content.{nom} import {nom}\n{nom}()", default_timeout=DELAI
    )


def sans_exception(at):
    """Message lisible si la page a levé une exception."""
    assert not at.exception, "\n\n".join(e.value for e in at.exception)
