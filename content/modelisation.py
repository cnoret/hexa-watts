import datetime
import streamlit as st
import joblib
import numpy as np
import pandas as pd

# Chargement du OneHotEncoder
encoder = joblib.load('models/encoder.joblib')

def preprocess(user_input):
    "Transformation des données de l'utilisateur"
    # Convertir les entrées utilisateur en dataframe
    input_df = pd.DataFrame([user_input])

    # L'ordre des colonnes doit également correspondre.
    expected_columns = ['Région', 'Jour', 'Mois', 'Jour_mois', 'Année', 'TMin (°C)', 
                        'TMax (°C)', 'TMoy (°C)', 'sin_heure', 'cos_heure']
    input_df = input_df.reindex(columns = expected_columns, fill_value = 0)

    # Affichage des données utilisateurs
    st.subheader("Prédiction : ")
    st.write("Données sélectionnées : ")
    st.dataframe(input_df, hide_index = True)

    # Encodage one-hot
    try:
        input_df_encoded = encoder.transform(input_df)
    except Exception as e:
        st.write(f"Une erreur s'est produite lors de l'encodage des données : {e}")
        return None
    return input_df_encoded

def get_user_input():
    "Collecte des données fournies par l'utilisateur"
    # Sélection du modèle
    choix_modele = st.selectbox("Choisissez un modèle", ["Régression Linéaire", "Régression Ridge"])

    st.subheader("Choix de la date et de la région")
    # Collecte des entrées de l'utilisateur
    region = st.selectbox("Région", [
        "Auvergne-Rhône-Alpes", 
        "Bourgogne-Franche-Comté", 
        "Bretagne", 
        "Centre-Val de Loire", 
        "Grand Est", 
        "Hauts-de-France", 
        "Île-de-France", 
        "Normandie", 
        "Nouvelle-Aquitaine", 
        "Occitanie", 
        "Pays de la Loire", 
        "Provence-Alpes-Côte d'Azur"
    ])

    # Choix de la date
    date = st.date_input('Date', value = datetime.date.today(),
                                  min_value=None, max_value=None, key=None, help=None, 
                                  on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", 
                                  disabled=False, label_visibility="visible")

    # Choix de l'heure
    heure = st.time_input("Heure", datetime.datetime.now())

    # Calcul de sin_heure et cos_heure
    heure_decimal = heure.hour + heure.minute / 60.0
    sin_heure = np.sin(2 * np.pi * heure_decimal / 24)
    cos_heure = np.cos(2 * np.pi * heure_decimal / 24)

    # Sélection des températures minimale, moyenne et maximale
    st.subheader("Sélection des températures")
    tmin = st.number_input("Température minimale (°C)")
    tmoy = st.number_input("Température moyenne (°C)")
    tmax = st.number_input("Température maximale (°C)")

    # Convertir la date en : Jour, Mois, Jour_mois, Année
    jour = date.strftime("%A")
    mois = date.strftime("%B")
    jour_mois = date.day
    annee = date.year

    # Dictionnaire avec les entrées de l'utilisateur
    user_input = {
        "Région": region,
        "Jour": jour,
        "Mois": mois,
        "Jour_mois": jour_mois,
        "Année": annee,
        "TMin (°C)": tmin,
        "TMax (°C)": tmax,
        "TMoy (°C)": tmoy,
        "sin_heure": sin_heure,
        "cos_heure": cos_heure,
    }
    return choix_modele, user_input

def modelisation():
    "Page de prédiction de l'application Streamlit"
    st.title("Modélisation et prédictions")
    st.image("images/ML.png", width = 250)
    st.subheader("Machine Learning")
    st.info("Nous avons entraîné deux modèles, qui permettent de faire des prédictions sur la \
            consommation d'électricité en France : la régression linéaire et la régression Ridge.\n \
            Vous devez sélectionner un des modèles, puis choisir une date et des températures afin \
            prédire la consommation en MW de cette future journée.", icon = "🤖")

    choix_modele, user_input = get_user_input()
    if st.button('Prédire la consommation électrique'):
        # Prétraitement des entrées de l'utilisateur
        features = preprocess(user_input)

        if features is not None:
            # Sélection du modèle et prédiction
            if choix_modele == 'Régression Linéaire':
                model = joblib.load("models/model_reglin.joblib")
            elif choix_modele == 'Régression Ridge':
                model = joblib.load("models/ridge_model_full.joblib")

            # Prédiction de la consommation d'énergie
            try:
                prediction = model.predict(features)
                st.warning(f"Consommation prédite : {round(prediction[0])} MW", icon = "🤖")
            except Exception as e:
                st.write(f"Une erreur s'est produite lors de la prédiction : {e}")

        # PLACEHOLDER METRICS
        # PLACEHOLDER CONCLUSION
    