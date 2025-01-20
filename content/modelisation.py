"""
Creation of the "Modélisation" page for the Hexa Watts application.
"""

import datetime
import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Load the model and encoder
@st.cache_resource
def load_model(filepath):
    """Load and cache the machine learning model."""
    return joblib.load(filepath)


@st.cache_resource
def load_encoder(filepath):
    """Load and cache the one-hot encoder."""
    return joblib.load(filepath)


# Load resources
encoder = load_encoder("models/encoder.joblib")
model = load_model("models/model_reglin.joblib")


def preprocess(user_input):
    """
    Preprocess the user input for model prediction.

    Args:
        user_input (dict): User-provided input data.

    Returns:
        np.array: Encoded and transformed features.
    """
    # Convert user input into a DataFrame
    input_df = pd.DataFrame([user_input])

    # Ensure column order matches the model
    expected_columns = ["Région", "Jour", "Mois", "Jour_mois", "Année", "TMin (°C)",
                        "TMax (°C)", "TMoy (°C)", "sin_heure", "cos_heure"]
    input_df = input_df.reindex(columns=expected_columns, fill_value=0)

    # Encode the input data
    try:
        input_df_encoded = encoder.transform(input_df)
    except Exception as e:
        st.error(f"Error during preprocessing: {e}")
        return None
    return input_df_encoded


def get_user_input():
    """
    Collect user input from the Streamlit interface.

    Returns:
        dict: Dictionary of user-provided input data.
    """
    st.subheader("Configuration de la prédiction")
    col1, col2 = st.columns([1, 1])

    with col1:
        # Region selection
        region = st.selectbox(
            "Région", [
                "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne",
                "Centre-Val de Loire", "Grand Est", "Hauts-de-France", "Île-de-France",
                "Normandie", "Nouvelle-Aquitaine", "Occitanie", "Pays de la Loire",
                "Provence-Alpes-Côte d'Azur"
            ]
        )

        # Date selection
        date = st.date_input("Date", value=datetime.date.today())

        # Temperature inputs
        st.markdown("### Températures (°C)")
        tmin = st.number_input("Température minimale", value=0.0, step=0.1)
        tmoy = st.number_input("Température moyenne", value=0.0, step=0.1)
        tmax = st.number_input("Température maximale", value=0.0, step=0.1)

    with col2:
        # Time selection
        heure = st.time_input("Heure", datetime.datetime.now())

        # Calculate time components
        heure_decimal = heure.hour + heure.minute / 60.0
        sin_heure = np.sin(2 * np.pi * heure_decimal / 24)
        cos_heure = np.cos(2 * np.pi * heure_decimal / 24)

        # Extract day, month, and year
        jour = date.strftime("%A")
        mois = date.strftime("%B")
        jour_mois = date.day
        annee = date.year

    # Return user input as a dictionary
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
    return user_input


def display_model_performance(y_true, y_pred):
    """
    Display the performance metrics of the model.

    Args:
        y_true (array-like): True target values.
        y_pred (array-like): Predicted target values.
    """
    st.subheader("📊 Performances du modèle")
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    col1, col2, col3 = st.columns(3)
    col1.metric("MAE (Mean Absolute Error)", f"{mae:.2f}")
    col2.metric("RMSE (Root Mean Squared Error)", f"{rmse:.2f}")
    col3.metric("R² (Coefficient de détermination)", f"{r2:.2f}")

    st.info(
        """
        - **MAE** : Moyenne des erreurs absolues entre les valeurs prédites et réelles.
        - **RMSE** : Racine carrée de la moyenne des erreurs quadratiques.
        - **R²** : Proportion de la variance expliquée par le modèle (1 = parfait).
        """
    )


def modelisation():
    """
    Main function to handle the "Modélisation" page.

    It collects user inputs, preprocesses the data, and displays the model prediction.
    """
    # Page title and introduction
    st.title("🔮 Modélisation et prédictions")
    st.image("images/ML.png", width=300)

    st.markdown(
        """
        Cette page vous permet de **prédire la consommation d'électricité** en France (en MW) 
        pour une date, une région et une plage horaire spécifiques. Le modèle utilisé est une 
        **régression linéaire** basée sur des données historiques.
        """
    )
    st.info(
        "Remplissez les champs ci-dessous pour configurer la prédiction, puis cliquez sur le bouton pour obtenir le résultat.",
        icon="⚡",
    )

    # Divider
    st.divider()

    # Collect user inputs
    user_input = get_user_input()

    # Divider
    st.divider()

    # Example performance data (for illustration)
    y_true_example = np.random.uniform(2000, 5000, 100)
    y_pred_example = y_true_example + np.random.normal(0, 300, 100)

    # Display model performance
    display_model_performance(y_true_example, y_pred_example)

    # Divider
    st.divider()

    # Prediction button
    if st.button("⚡ Prédire la consommation électrique"):
        # Preprocess the user input
        features = preprocess(user_input)
        if features is not None:
            try:
                # Predict electricity consumption
                prediction = model.predict(features)
                st.success(
                    f"🌟 Consommation prédite : **{round(prediction[0], 2)} MW**",
                    icon="🔮",
                )
            except Exception as e:
                st.error(f"Prediction error: {e}")
