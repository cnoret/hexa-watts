"""
Création de la page "Ressources" de l'application Énergie_France
"""

import streamlit as st

def ressources():
    "Contenu de la page"
    st.title("Sources des données")
    st.markdown("""
                Les données utilisées dans ce projet proviennent de diverses sources publiques.
                - **Consommation énergétique des régions (janvier 2013 à mai 2022)** : [eco2mix-regional-cons-def](https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def)
                - **Population Française par région** : [INSEE Statistiques](https://www.insee.fr/fr/statistiques)
                - **Températures régionales** : [Météo France](https://donneespubliques.meteofrance.fr)
                - **Bilans énergétiques (Europe)** : [Eurostat](https://ec.europa.eu/eurostat/fr)
                """)

    st.title("Compétences et technologies")
    st.subheader('Python')
    st.markdown("""
                Les bibliothèques Python suivantes ont été utilisées dans ce projet :
                - **[Pandas](https://pandas.pydata.org/)** : Utilisé pour la manipulation des données et l'analyse.
                - **[Matplotlib](https://matplotlib.org/)** : Utilisé pour la création de visualisations statiques, animées et interactives.
                - **[Seaborn](https://seaborn.pydata.org/)** : Basé sur Matplotlib, Seaborn fournit une interface de haut niveau pour dessiner des graphiques statistiques attrayants.
                - **[Plotly](https://plotly.com/python/)** : Utilisé pour les visualisations interactives.
                - **[Scikit-Learn](https://scikit-learn.org/stable/)** : Utilisé pour la modélisation des données, y compris la préparation, le prétraitement et la prédiction.
                - **[Streamlit](https://streamlit.io/)** : Streamlit permet de transformer des scripts de données en applications web partageables.
                """)

    st.subheader('Déploiement')
    st.markdown("""
                Les outils suivants ont été utilisés pour le déploiement de ce projet :
                - **[Streamlit Cloud](https://streamlit.io/cloud)** : Utilisé pour le déploiement de l'application en ligne.
                - **[GitHub](https://github.com/)** : Utilisé pour le contrôle de version et le stockage du code de l'application.
                """)
