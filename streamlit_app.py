import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image

def display_intro():
    st.title("Titre du projet énergie à définir")
    st.subheader("Analyse et prédiction de la consommation \
                 électrique en France")
    st.write("Projet réalisé par Titi, Tata, Toto et Tutu")
    code = "print('Hello Team !')"
    st.code(code, language = 'python')


if __name__ == "__main__":
    st.set_page_config(page_title = "Consommation d'électricité en France")
    with st.sidebar:
        choice = option_menu(
        menu_title = "Le Projet",
        options=["Intro", 
                 "Explo", 
                 "Analyses et visualisations", 
                 "Prédictions", 
                 "Conclusion", 
                 "Data"],
        default_index=0)

display_intro()
