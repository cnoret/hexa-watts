# Packages
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image


def introduction():
    image_top = Image.open("images/nucleaire.jpeg")
    st.image(image_top, caption = "Centrale nucléaire de Saint Laurent des Eaux \
             - Photo : Sipa / Patrick SICCOLI", width = 500)
    st.title("Projet ")
    st.subheader("Analyse et prédiction de la consommation électrique en France")

    st.subheader("Contexte")
    st.write("TEXT")

    st.subheader("Objectifs de l'analyse")
    st.write("TEXT")

def exploration():
    st.title("Exploration des données")

def preparation():
    st.title("Préparation des données")

def visualisation():
    st.title("Analyses et visualisations")

def modelisation():
    st.title("Modélisation et prédictions")

def conclusion():
    st.title("Conclusion")

def ressources():
    st.title("Ressources")


# Page title and favicon
st.set_page_config(page_title = "Consommation d'électricité en France",
                   page_icon = "images/favicon.png")

# Sidebar menu
with st.sidebar:
    image_side = Image.open("images/triangle.png")
    st.image(image_side)
    st.header("Energie_France")
    choice = option_menu(
        menu_title = "Sommaire",
        options = ["Introduction",
                   "Exploration des données",
                   "Préparation des données",
                   "Analyses et visualisations",
                   "Modélisation et prédictions",
                   "Conclusion",
                   "Ressources"],
        default_index = 0)
    st.header("Equipe du projet :")
    st.markdown('- Christophe NORET&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret) \
                [<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret)', unsafe_allow_html=True)
    st.markdown('- Siham HOUCHI&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret) \
                [<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret)', unsafe_allow_html=True)
    st.markdown('- Cyril LECAILLE&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret) \
                [<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret)', unsafe_allow_html=True)
    st.markdown('- Simon BERRY&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret) \
                [<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret)', unsafe_allow_html=True)


if choice == "Introduction":
    introduction()

elif choice == "Exploration des données":
    exploration()

elif choice == "Préparation des données":
    preparation()

elif choice == "Analyses et visualisations":
    visualisation()

elif choice == "Modélisation et prédictions":
    modelisation()

elif choice == "Conclusion":
    conclusion()

else:
    ressources()
    