"""
Création de la page "Introduction" de l'application Énergie_France
"""

import streamlit as st
from PIL import Image

def introduction():
    "Contenu de la page d'accueil"
    image_top = Image.open("images/nucleaire.jpeg")
    st.image(image_top, caption = "Centrale nucléaire de Saint Laurent des Eaux \
             - Photo : Sipa / Patrick SICCOLI", width = 500)
    st.subheader("Analyse et prédiction de la consommation électrique en France")

    st.subheader("Contexte")
    st.write("La problématique de notre projet consiste à comprendre et à anticiper le phasage entre la consommation et la production énergétique au niveau national \
        et régional afin d'observer, analyser et prédire des déséquilibres importants entre l'offre et la demande.")
    st.write("Dans cette analyse, nous allons nous poser plusieurs questions :")
    st.write("* Comment identifier et analyser les variations de consommation au niveau régional ?")
    st.write("* Comment évaluer la production des différentes fillières énergétique ?")
    st.write("* Comment les énergies renouvelables sont-elle réparties géographiquement et quel impact ont-elles ? ")
    st.write("* Pouvons-nous prédire la consommation future afin d'éviter un blackout ?")
    st.write("En répondant à ces questions, nous pourrons prévoir précisement les futurs besoins énergétiques \
             et anticiper les périodes à risques afin de pouvoir prendre des mesures préventives sur le réseau électrique.")
    st.write("Notre projet vise donc à exploiter certaines données spécifiques afin de mieux comprendre et gérer les différents équilibres énergiques.")
    st.error("Nous nous insérons dans ce domaine sans connaissance réelle du domaine de l'énergétique et nous devrons également acquérir les connaissances spécifiques liées à la production d'électricité en France.")

    st.subheader("Objectifs de l'analyse")
    st.write("* Analyser les données de consommation électrique afin d'identifier des tendances et des schémas de consommation")
    st.write("* Analyser et comparer les différentes filières de production (Nucléaire/Renouvelable)")
    st.write("* Visualiser la localisation et la capacitée de production des énergies renouvelables")
    st.write("* Développer des modèles prédictifs permettant d'estimer les consommations futures afin d'anticiper les périodes à risque.")
