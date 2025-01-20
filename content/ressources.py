"""
Creation of the "Ressources" page for the Hexa Watts application
"""

import streamlit as st


def ressources():
    """Content of the resources page"""

    # Title: Sources des données
    st.title("📚 Sources des données")
    st.markdown(
        """
        Les données utilisées dans ce projet proviennent de diverses sources publiques, toutes accessibles gratuitement :
        """
    )
    st.markdown(
        """
        - **[eco2mix-regional-cons-def](https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def)** : Consommation énergétique des régions (janvier 2013 à mai 2022).
        - **[INSEE Statistiques](https://www.insee.fr/fr/statistiques)** : Population Française par région.
        - **[Météo France](https://donneespubliques.meteofrance.fr)** : Températures régionales.
        - **[Eurostat](https://ec.europa.eu/eurostat/fr)** : Bilans énergétiques en Europe.
        - **[Carte des régions de France (GeoJSON)](https://france-geojson.gregoiredavid.fr/)** : Fournie par Grégoire David.
        """
    )

    st.divider()

    # Title: Compétences et Technologies
    st.title("🔧 Compétences et technologies")
    st.markdown("### Langage Python 🐍", unsafe_allow_html=True)
    st.markdown(
        """
        Les bibliothèques suivantes ont été utilisées dans ce projet :
        - **[Pandas](https://pandas.pydata.org/)** : Manipulation et analyse des données.
        - **[Matplotlib](https://matplotlib.org/)** : Visualisations statiques, animées et interactives.
        - **[Seaborn](https://seaborn.pydata.org/)** : Graphiques statistiques attrayants.
        - **[Plotly](https://plotly.com/python/)** : Visualisations interactives et dynamiques.
        - **[Scikit-Learn](https://scikit-learn.org/stable/)** : Préparation des données et modélisation prédictive.
        - **[Streamlit](https://streamlit.io/)** : Transformation des scripts Python en applications web.
        - **[Geopandas](https://geopandas.org/en/stable/)** : Manipulation et visualisation de données géospatiales.
        """
    )

    st.divider()

    # Development and Deployment Tools
    st.subheader("💻 Développement et déploiement")
    st.markdown(
        """
        Les outils suivants ont été essentiels au développement et au déploiement du projet :
        - **[Jupyter Notebook](https://jupyter.org/)** : Programmation interactive et exploratoire.
        - **[Google Colab](https://colab.research.google.com/)** : Notebooks collaboratifs exécutés dans le cloud.
        - **[Visual Studio Code](https://code.visualstudio.com/)** : Éditeur de code puissant et extensible.
        - **[Git](https://git-scm.com/)** : Système de contrôle de version.
        - **[Streamlit Cloud](https://streamlit.io/cloud)** : Plateforme de déploiement en ligne pour Streamlit.
        - **[GitHub](https://github.com/)** : Plateforme pour le contrôle de version et le stockage du code source.
        """
    )

    st.divider()

    # Thank You Section
    st.title("🙏 Remerciements")
    st.markdown(
        """
        Merci à toutes les organisations et plateformes qui fournissent des données ouvertes et des outils
        qui rendent possibles des projets comme celui-ci. Un merci spécial à la communauté Python pour ses
        bibliothèques open source et à Streamlit pour avoir permis de transformer ces analyses en une application
        web accessible à tous.
        """
    )
