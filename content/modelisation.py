import streamlit as st
import joblib 
import pandas as pd
from datetime import datetime

def modelisation():
    st.title("Modélisation et prédictions")
    st.image("images/ML.png", width= 250)

    #Instructions
    st.info("Nous avons entraîné deux modèles, qui permettent de faire des prédictions sur la consommation d'électricité en France. Vous devez sélectionner un des modèles, puis une date pour obtenir une prédiction.", icon= "🤖")

    # Charger les données depuis un fichier CSV ("temp.csv" dans votre cas)
    temp = pd.read_csv("datasets/temp.csv", sep = ';')

    # Convertir la colonne 'Date' en format de date
    temp['Date'] = pd.to_datetime(temp['Date'], format='%d/%m/%Y')

    # Créer une application Streamlit
    st.title("Calcul de moyenne de température pour une date future")

    # Sélection de la date future
    date_future = st.date_input("Sélectionnez une date future", min_value=temp['Date'].max())

    # Sélection de la région
    regions = temp['Région'].unique()
    selected_region = st.selectbox("Sélectionnez une région", regions)

    # Filtrage des données pour la région
    filtered_data = temp[temp['Région'] == selected_region]

    # Date de la date future (jour et mois)
    date_future_month_day = date_future.strftime('%m-%d')

    # Liste des années à considérer
    annees = [2016, 2017, 2018, 2019, 2020, 2021]

    # Calcul des moyennes pour la même date sur les années spécifiées
    moyennes_tmin = []
    moyennes_tmax = []
    moyennes_tmoy = []

    for annee in annees:
        date_annee = datetime(annee, date_future.month, date_future.day)
        filtered_data_annee = filtered_data[filtered_data['Date'].dt.month == date_annee.month]
        filtered_data_annee = filtered_data_annee[filtered_data_annee['Date'].dt.day == date_annee.day]
        moyennes_tmin.append(filtered_data_annee['TMin (°C)'].mean())
        moyennes_tmax.append(filtered_data_annee['TMax (°C)'].mean())
        moyennes_tmoy.append(filtered_data_annee['TMoy (°C)'].mean())

    # Afficher les résultats
    st.write(f"Moyenne TMin pour {selected_region} le {date_future.strftime('%d/%m')}:")
    for i, annee in enumerate(annees):
        st.write(f"{annee}: {moyennes_tmin[i]:.2f} °C")

    st.write(f"Moyenne TMax pour {selected_region} le {date_future.strftime('%d/%m')}:")
    for i, annee in enumerate(annees):
        st.write(f"{annee}: {moyennes_tmax[i]:.2f} °C")

    st.write(f"Moyenne TMoy pour {selected_region} le {date_future.strftime('%d/%m')}:")
    for i, annee in enumerate(annees):
        st.write(f"{annee}: {moyennes_tmoy[i]:.2f} °C")









    # #Selection du modèle
    # choix_modele = st.selectbox("Choix du modèle", ['Régression Linéaire', 'Ridge'])

    # # Sélection de la date
    # selected_date = st.date_input('Date pour la prédiction', value="today", min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", disabled=False, label_visibility="visible")

    # if choix_modele == 'Régression Linéaire':
    #     # Import modèle
    #     model_reglin = joblib.load(filename="./models/line_reg_model_full.joblib")

    #     # Prediction
    #     prediction = model_reglin.predict(selected_date)
    #     st.write(f"Résultat de la prédiction: {prediction}")

    # elif choix_modele == 'Ridge':
    #     # Import modèle
    #     model_ridge = joblib.load(filename="./models/ridge_model_full.joblib")

    #     # Prediction
    #     prediction = model_ridge.predict(selected_date)
    #     st.write(f"Résultat de la prédiction: {prediction}")