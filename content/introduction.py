"""
Creation of the "Introduction" page for the Hexa Watts application
"""

import json
from pathlib import Path

import streamlit as st

from content.interface import en_tete, indicateurs, nombre_fr

CHEMIN_METRIQUES = "models/metriques.json"

# Les images sont passées à st.image par leur chemin : Streamlit lit le fichier
# à chaque affichage. Un objet PIL mis en cache avec st.cache_resource serait
# partagé entre les sessions, et deux lectures simultanées du même fichier
# provoquent l'erreur « image file is truncated ».


def introduction():
    """Content of the introduction page"""
    metriques = json.loads(Path(CHEMIN_METRIQUES).read_text(encoding="utf-8"))

    texte, photo = st.columns([3, 2], gap="large", vertical_alignment="center")
    with texte:
        en_tete(
            "Analyse et prédiction de la consommation électrique en France",
            surtitre="Hexa Watts · Projet data énergie",
            sous_titre="Neuf années de données RTE, douze régions, six filières de "
            "production et un modèle qui prédit la consommation à la demi-heure.",
        )
        indicateurs(
            [
                ("Années étudiées", "9", "de 2013 à 2021"),
                ("Régions", "12", "métropole"),
                ("Erreur du modèle", f"{nombre_fr(metriques['test']['mape'] * 100, 1)} %",
                 "MAPE sur 1 an"),
            ]
        )
    with photo:
        try:
            st.image(
                "images/nucleaire.jpeg",
                caption=(
                    "Centrale nucléaire de Saint Laurent des Eaux - "
                    "Photo : Sipa / Patrick SICCOLI"
                ),
                width="stretch",
            )
        except FileNotFoundError:
            st.warning("L'image de la centrale nucléaire n'a pas pu être chargée.")

    st.divider()

    contexte, objectifs = st.columns([3, 2], gap="large")
    with contexte:
        # Context section
        st.subheader("Contexte")
        st.markdown(
            """
            La problématique de notre projet consiste à **comprendre et à anticiper le phasage** entre
            la consommation et la production énergétique au niveau national et régional afin d'observer,
            analyser et prédire des déséquilibres importants entre l'offre et la demande.

            Dans cette analyse, nous allons nous poser plusieurs questions :
            - Comment identifier et analyser les variations de consommation au niveau régional ?
            - Comment évaluer la production des différentes filières énergétiques ?
            - Comment les énergies renouvelables sont-elles réparties géographiquement et quel impact
              ont-elles ?
            - Pouvons-nous prédire la consommation future afin d'éviter un black-out ?

            En répondant à ces questions, nous pourrons prévoir précisément les futurs besoins
            énergétiques et anticiper les périodes à risques, permettant de prendre des mesures
            préventives sur le réseau électrique.

            Notre projet vise donc à exploiter certaines données spécifiques afin de mieux comprendre
            et gérer les différents équilibres énergétiques.
            """
        )
        # Add a note about the team's expertise
        st.info(
            "Note : Nous nous insérons dans ce domaine sans connaissance réelle de l'énergie. "
            "Nous devrons acquérir des compétences spécifiques liées à la production d'électricité "
            "en France."
        )

    with objectifs:
        # Objectives section
        st.subheader("Objectifs de l'analyse")
        st.markdown(
            """
            - Analyser les données de consommation électrique afin d'identifier des tendances et
              des schémas de consommation.
            - Analyser et comparer les différentes filières de production (Nucléaire/Renouvelable).
            - Visualiser la localisation et la capacité de production des énergies renouvelables.
            - Développer des modèles prédictifs permettant d'estimer les consommations futures afin
              d'anticiper les périodes à risque.
            """
        )

    # Key information section
    st.info(
        "Cette application vise à fournir des insights sur les tendances énergétiques en France "
        "en combinant analyse exploratoire et modélisation prédictive."
    )
