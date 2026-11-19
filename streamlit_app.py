"""
Streamlit Start
"""

import os

# Doit être défini avant le premier import de pyarrow : l'allocateur système
# rend la mémoire libérée, contrairement à celui d'Arrow par défaut. Cela
# compte sur Streamlit Community Cloud, où la mémoire est limitée.
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")

# External libraries
import streamlit as st
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Hexa Watts",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Internal modules
from content.introduction import introduction
from content.exploration import exploration
from content.preparation import preparation
from content.visualisation import visualisation
from content.modelisation import modelisation
from content.conclusion import conclusion
from content.ressources import ressources

# Sidebar header and menu
with st.sidebar:
    # App header
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>⚡ Hexa Watts ⚡</h1>
            <p style='font-size: 14px;'>Analyse et prédiction de la consommation énergétique</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Image in the sidebar
    try:
        st.image("images/triangle.png")
    except FileNotFoundError:
        st.warning("L'image de la sidebar n'a pas été trouvée.")

    # Navigation menu
    st.header("Sommaire")
    choice = option_menu(
        menu_title="Navigation",
        options=[
            "🏠 Introduction",
            "🔍 Exploration des données",
            "🛠 Préparation des données",
            "📊 Analyses et visualisations",
            "🤖 Modélisation et prédictions",
            "📜 Conclusion",
            "📚 Ressources",
        ],
        default_index=0,
    )

    st.sidebar.header("Équipe du projet Énergie France :")
    team = [
        {
            "name": "Simon BERRY",
            "linkedin": "https://www.linkedin.com/in/simon-berry56/",
            "github": "https://github.com/sibmel29",
        },
        {
            "name": "Siham HOUCHI",
            "linkedin": "https://www.linkedin.com/in/siham-houchi-19622a15a/",
        },
        {
            "name": "Christophe NORET",
            "linkedin": "http://www.linkedin.com/in/cnoret",
            "github": "https://github.com/cnoret",
        },
    ]

    for member in team:
        linkedin_logo = (
            f"<a href='{member['linkedin']}' target='_blank'>"
            f"<img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg' width='20' style='vertical-align:middle;'></a>"
            if "linkedin" in member
            else ""
        )
        github_logo = (
            f"<a href='{member['github']}' target='_blank'>"
            f"<img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' width='20' style='vertical-align:middle;'></a>"
            if "github" in member
            else ""
        )
        st.markdown(
            f"""
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <span style='margin-right: 10px; font-weight: bold;'>{member['name']}</span>
            {linkedin_logo}
            <span style='margin-left: 10px;'>{github_logo}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
    <hr>
    <p style='font-size: 14px; text-align: center;'>
        <strong>Refonte (Hexa Watts)</strong> réalisée par :
        <span style='font-weight: bold;'>Christophe NORET</span>
    </p>
    """,
        unsafe_allow_html=True,
    )
# Pages mapping
pages = {
    "🏠 Introduction": introduction,
    "🔍 Exploration des données": exploration,
    "🛠 Préparation des données": preparation,
    "📊 Analyses et visualisations": visualisation,
    "🤖 Modélisation et prédictions": modelisation,
    "📜 Conclusion": conclusion,
    "📚 Ressources": ressources,
}

# Dynamically load the selected page
page = pages.get(choice, None)
if page:
    with st.spinner(f"Chargement de la page {choice}..."):
        page()
else:
    st.error("Page non trouvée.")
