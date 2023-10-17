import streamlit as st
import joblib 

def modelisation():
    st.title("Modélisation et prédictions")
    st.image("images/ML.png", width= 250)

    #Instructions
    st.info("Nous avons entraîné deux modèles, qui permettent de faire des prédictions sur la consommation d'électricité en France. Vous devez sélectionner un des modèles, puis une date pour obtenir une prédiction.", icon= "🤖")

    #Selection du modèle
    choix_modele = st.selectbox("Choix du modèle", ['Régression Linéaire', 'Ridge'])

    # Sélection de la date
    selected_date = st.date_input('Date pour la prédiction', value="today", min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", disabled=False, label_visibility="visible")

    if choix_modele == 'Régression Linéaire':
        # Import modèle
        model_reglin = joblib.load(filename="./models/line_reg_model_full.joblib")

        # Prediction
        prediction = model_reglin.predict(selected_date)
        st.write(f"Résultat de la prédiction: {prediction}")

    elif choix_modele == 'Ridge':
        # Import modèle
        model_ridge = joblib.load(filename="./models/ridge_model_full.joblib")

        # Prediction
        prediction = model_ridge.predict(selected_date)
        st.write(f"Résultat de la prédiction: {prediction}")