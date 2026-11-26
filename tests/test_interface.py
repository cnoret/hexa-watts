"""Éléments d'interface communs (content/interface.py) et filtres de la page Analyses."""

import json

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


def test_mettre_en_avant_grise_les_autres_regions():
    import plotly.express as px
    import pandas as pd

    from content.interface import GRIS_SECONDAIRE, mettre_en_avant

    df = pd.DataFrame({"x": [1, 2, 1, 2], "y": [3, 4, 5, 6], "Région": ["A", "A", "B", "B"]})
    fig = mettre_en_avant(px.line(df, x="x", y="y", color="Région"), "B")
    lignes = {t.name: t for t in fig.data}
    assert lignes["A"].line.color == GRIS_SECONDAIRE
    assert lignes["B"].line.width == 4


def test_analyses_filtres_periode_et_region():
    """Les filtres de la barre latérale changent les indicateurs sans erreur."""
    from tests.conftest import page_app

    at = page_app("visualisation").run()
    sans_exception(at)
    at.slider(key="analyses_periode").set_value((2016, 2019)).run()
    sans_exception(at)
    assert any(m.label == "Production 2019" for m in at.metric)
    at.selectbox(key="analyses_region").set_value("Grand Est").run()
    sans_exception(at)
    # La carte des échanges et le solde de la région choisie s'affichent
    specs = " ".join(c.proto.spec for c in at.get("plotly_chart"))
    for titre in ["Régions importatrices en rouge", "Solde annuel des échanges physiques : Grand Est"]:
        assert json.dumps(titre)[1:-1] in specs, titre


def test_analyses_2021_seule_sans_echanges():
    """Les échanges de 2021 ne sont pas exploitables : un message remplace la carte."""
    from tests.conftest import page_app

    at = page_app("visualisation").run()
    at.slider(key="analyses_periode").set_value((2021, 2021)).run()
    sans_exception(at)
    assert any("2021" in i.value for i in at.info)
