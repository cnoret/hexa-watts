"""Éléments d'interface communs (content/interface.py)."""

from streamlit.testing.v1 import AppTest

from content.interface import nombre_fr
from tests.conftest import DELAI, RACINE, sans_exception


def test_nombre_fr():
    assert nombre_fr(1234.5) == "1 234"
    assert nombre_fr(69.54, 1) == "69,5"
    assert nombre_fr(-4.12, 1, signe=True) == "−4,1"
    assert nombre_fr(4.8, 1, signe=True) == "+4,8"


def test_navigation_une_adresse_par_page():
    """Chaque page du menu a sa propre adresse, et l'accueil est l'Introduction."""
    at = AppTest.from_file(str(RACINE / "streamlit_app.py"), default_timeout=DELAI).run()
    sans_exception(at)
    source = (RACINE / "streamlit_app.py").read_text(encoding="utf-8")
    for chemin in ["exploration", "preparation", "analyses", "modelisation",
                   "conclusion", "ressources"]:
        assert f'url_path="{chemin}"' in source
    assert at.title[0].value.startswith("Analyse et prédiction")


def test_graphique_fond_transparent():
    """graphique() laisse le fond de la carte visible derrière la figure."""
    at = AppTest.from_string(
        "import plotly.graph_objects as go\n"
        "from content.interface import graphique\n"
        "graphique(go.Figure(go.Bar(x=[1, 2], y=[3, 4], name='a')))\n",
        default_timeout=DELAI,
    ).run()
    sans_exception(at)
    spec = at.get("plotly_chart")[0].proto.spec
    assert "rgba(0,0,0,0)" in spec.replace(" ", "")
