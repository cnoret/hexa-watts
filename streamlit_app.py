import streamlit as st
import pandas as pd
from PIL import Image

def display_intro():
    st.subheader("Analyse et prédiction de la consommation \
                 électrique en France")
    st.write("Projet réalisé par Titi, Tata, Toto et Tutu")
    code = "print('Hello Team !')"
    st.code(code, language = 'python')


if __name__ == "__main__":
    st.set_page_config(
        page_title = "Consommation d'électricité en France",
        layout = "centered"
    )

st.title("Titre du projet énergie à définir")
display_intro()
