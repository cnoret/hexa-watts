"""
Creation of the "Preparation" page for the Hexa Watts application
"""

import streamlit as st


def preparation():
    """Content of the data preparation page"""

    # Page title
    st.title("Préparation des données : DF (Eco2Mix)")

    # Handling missing values
    st.header("Traitement des valeurs manquantes")
    st.info(
        "Notre jeu de données est très propre, les NaNs présents correspondent uniquement "
        "à une production ou consommation nulle. Nous avons procédé en découpage par étage "
        "afin de traiter séparément ces valeurs. Nous n'avons pas de duplicatas.",
        icon="✨",
    )

    # Modifications and new columns
    st.header("Modification et ajout de nouvelles colonnes")
    st.write(
        " - Ajout de colonnes temporelles avec DateTime ('Date - Heure', 'Jour', 'Jour_mois', 'Mois', "
        "'Année').\n"
        " - Création d'une colonne booléenne 'Week-end'.\n"
        " - Suppression de l'année 2022 du scope, car elle n'était pas complète dans l'étude.\n"
        " - Création d'une colonne qui somme toute la 'Production (MW)'.\n"
        " - Création d'une colonne 'Côtier' pour observer les tendances des régions côtières.\n"
        " - Création d'une fonction qui sépare les régions du Nord de celles du Sud."
    )

    # Creation of datasets
    st.header("Création de nos jeux de données")
    st.write(
        "Notre stratégie a été de créer des jeux de données depuis DF, pour faciliter la suite de l'étude "
        "et les visualisations :\n"
        " - 'consommation' = Toutes les données sans les données de production.\n"
        " - 'production' = Toutes les données sans la consommation.\n"
        " - 'yearly' = Un groupby sur 'Année' et 'Région', avec SUM de Consommation.\n"
        " - 'tco_tch' = Nous avons traité toutes ces valeurs dans leur propre DataFrame."
    )

    # Preparation of INSEE data
    st.header("Préparation des données de l'INSEE")
    st.write(
        "Les données étaient sur un fichier Excel. Nous avons utilisé 'XLRD', la méthode GLOBALS(), "
        "et des boucles pour extraire ces données dans un DataFrame exploitable.\n\n"
        "Par la suite, les données de la population des différentes régions par années ont été ajoutées "
        "à notre DF 'yearly', puis nous avons créé le ratio 'Consommation per Capita', baptisé 'ratio'."
    )

    # Preparation of EUROSTAT data
    st.header("Préparation des données de EUROSTAT")
    st.write(
        "Le fichier récupéré auprès de EUROSTAT était très formaté, il a donc nécessité plusieurs "
        "transformations :\n"
        " - Une fonction pour déterminer le 'type' (consommation, production, imports, etc.).\n"
        " - Une fonction pour déterminer la 'class' (type d'énergie).\n"
        " - Renommage complet des colonnes.\n"
        " - Conversion des noms de pays du format ISO2 au format complet.\n"
        " - Séparation en deux DataFrames : EUROPE_CONS et EUROPE_PROD."
    )

    # Color codes for visualizations
    st.header("Nos codes couleurs")
    st.write(
        "Nous avons créé deux dictionnaires pour garder des couleurs constantes dans les visualisations :"
    )

    colors = {
        "Thermique (MW)": "red",
        "Nucléaire (MW)": "#F7E237",
        "Eolien (MW)": "lightblue",
        "Solaire (MW)": "orange",
        "Hydraulique (MW)": "darkblue",
        "Bioénergies (MW)": "green",
    }

    st.code(colors, language="python")

    colors_euro = {
        "Bioénergie": "#FF0000",  # Red
        "Déchets municipaux renouvelables": "#00FF00",  # Green
        "Éolien": "#ADD8E6",  # Light blue
        "Solaire Photovoltaique": "#FFA500",  # Orange
        "Solaire Thermique": "#FFFF00",  # Yellow
        "Hydraulique": "#00008B",  # Dark blue
        "Biogaz": "#808080",  # Gray
        "Biocarburants": "#800080",  # Purple
        "Pompe à chaleur": "#FF0000",  # Red
        "Océan": "#0000FF",  # Blue
        "Geothermique": "#D076FF",  # Light purple
    }

    st.code(colors_euro, language="python")
