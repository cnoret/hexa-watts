"""
Creation of the "Introduction" page for the Hexa Watts application
"""

import streamlit as st
from PIL import Image


# Cache for loading images
@st.cache_resource
def load_image(filepath):
    """Load an image using PIL"""
    return Image.open(filepath)


def introduction():
    """Content of the introduction page"""
    try:
        # Load and display the main image
        image_top = load_image("images/nucleaire.jpeg")
        st.image(
            image_top,
            caption=(
                "Centrale nucléaire de Saint Laurent des Eaux - "
                "Photo : Sipa / Patrick SICCOLI"
            ),
            use_container_width=True,
        )
    except FileNotFoundError:
        # Show a warning if the image is not found
        st.warning("L'image de la centrale nucléaire n'a pas pu être chargée.")

    # Page title
    st.title("Analyse et prédiction de la consommation électrique en France")

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
    # Add an error note about the team's expertise
    st.error(
        "Note : Nous nous insérons dans ce domaine sans connaissance réelle de l'énergie. "
        "Nous devrons acquérir des compétences spécifiques liées à la production d'électricité "
        "en France."
    )

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
