import streamlit as st
from PIL import Image

def introduction():
    "Landing page"
    image_top = Image.open("images/nucleaire.jpeg")
    st.image(image_top, caption = "Centrale nucléaire de Saint Laurent des Eaux \
             - Photo : Sipa / Patrick SICCOLI", width = 500)
    st.title("Projet ")
    st.subheader("Analyse et prédiction de la consommation électrique en France")

    st.subheader("Contexte")
    st.write("TEXT")

    st.subheader("Objectifs de l'analyse")
    st.write("TEXT")
