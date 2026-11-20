"""
Creation of the "Preparation" page for the Hexa Watts application
"""

import pprint

import streamlit as st

from content.couleurs import COULEURS_EUROPE, COULEURS_FILIERES


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

    st.code(
        "COULEURS_FILIERES = " + pprint.pformat(COULEURS_FILIERES, sort_dicts=False),
        language="python",
    )
    st.code(
        "COULEURS_EUROPE = " + pprint.pformat(COULEURS_EUROPE, sort_dicts=False),
        language="python",
    )
