"""Chaque page de l'application s'exécute sans exception."""

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import DELAI, PAGES, RACINE, page_app, sans_exception


def test_application_demarre():
    at = AppTest.from_file(str(RACINE / "streamlit_app.py"), default_timeout=DELAI).run()
    sans_exception(at)
    assert not at.error
    # La page d'accueil (Introduction) est affichée par défaut
    assert at.title


@pytest.mark.parametrize("nom", PAGES)
def test_page_sans_exception(nom):
    at = page_app(nom).run()
    sans_exception(at)
    assert not at.error, [e.value for e in at.error]
    assert at.title, f"La page {nom} n'affiche pas de titre"


def test_pages_du_menu():
    """Le menu de streamlit_app.py pointe bien vers les 7 pages testées ici."""
    source = (RACINE / "streamlit_app.py").read_text(encoding="utf-8")
    for nom in PAGES:
        assert f"from content.{nom} import {nom}" in source


def test_visualisation_toutes_les_options():
    """Chaque choix des listes déroulantes de la page Analyses s'affiche sans erreur."""
    at = page_app("visualisation").run()
    sans_exception(at)
    for i in range(len(at.selectbox)):
        for option in at.selectbox[i].options:
            at.selectbox[i].set_value(option).run()
            sans_exception(at)
