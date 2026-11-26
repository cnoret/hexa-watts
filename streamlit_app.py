"""
Point d'entrée de l'application Hexa Watts.
"""

import os

# Doit être défini avant le premier import de pyarrow : l'allocateur système
# rend la mémoire libérée, contrairement à celui d'Arrow par défaut. Cela
# compte sur Streamlit Community Cloud, où la mémoire est limitée.
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")

import streamlit as st

st.set_page_config(
    page_title="Hexa Watts",
    page_icon="images/icone.svg",
    layout="wide",
    initial_sidebar_state="auto",
)

# Pages de l'application
from content.introduction import introduction
from content.exploration import exploration
from content.preparation import preparation
from content.visualisation import visualisation
from content.modelisation import modelisation
from content.conclusion import conclusion
from content.ressources import ressources
from content.interface import appliquer_style, pied_de_page

appliquer_style()
st.logo("images/logo.svg", size="large")

# Navigation dans la barre latérale : chaque page a sa propre adresse
# (par exemple /analyses), que l'on peut partager ou mettre en favori.
page = st.navigation(
    [
        st.Page(introduction, title="Introduction", icon=":material/home:", default=True),
        st.Page(exploration, title="Exploration", icon=":material/search:", url_path="exploration"),
        st.Page(preparation, title="Préparation", icon=":material/build:", url_path="preparation"),
        st.Page(visualisation, title="Analyses", icon=":material/bar_chart:", url_path="analyses"),
        st.Page(modelisation, title="Modélisation", icon=":material/model_training:", url_path="modelisation"),
        st.Page(conclusion, title="Conclusion", icon=":material/flag:", url_path="conclusion"),
        st.Page(ressources, title="Ressources", icon=":material/menu_book:", url_path="ressources"),
    ],
    position="sidebar",
)
page.run()

pied_de_page()
