import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image


def display_intro():
    """ Page d'introduction au projet"""

    image_top = Image.open("images/nucleaire.jpeg")
    st.image(image_top)
    st.title("Energie_France")
    st.subheader("Analyse et prédiction de la consommation \
                 électrique en France")
    st.write("Par Christophe NORET, Siham HOUCHI, Cyril LECAILLE et Simon BERRY")

    st.subheader("But du projet")
    st.write("TEXT")

    st.subheader("Objectifs de l'analyse")
    st.write("TEXT")

    st.subheader("Outils et compétences utilisées")
    st.write("TEXT")


# Titre de la page dans l'onglet du navigateur Web
st.set_page_config(page_title = "Consommation d'électricité en France",
                   page_icon = "images/favicon.png")

# Création de la barre latérale
with st.sidebar:
    # Ouverture puis affichage du logo de la barre latérale
    image_side = Image.open("images/triangle.png")
    st.image(image_side)

    # Header correspondant au nom du projet
    st.header("Energie_France")

    # Création du menu et de ses catégories
    choice = option_menu(
        menu_title = "Menu",
        options = ["Introduction du projet",
                   "Exploration des données",
                   "Analyses et visualisations",
                   "Prédictions",
                   "Conclusion",
                   "Liens et ressources"],
        default_index = 0)

    # Bloc de l'équipe
    st.write("Equipe du projet :")
    st.subheader("- Christophe NORET")
    st.write("LinkedIn / Github")
    st.subheader("- Siham HOUCHI")
    st.write("LinkedIn / Github")
    st.subheader("- Cyril LECAILLE")
    st.write("LinkedIn / Github")
    st.subheader("- Simon Berry")
    st.write("LinkedIn / Github")

display_intro()
