"""
Creation of the "Modélisation" page for the Hexa Watts application.
"""

import datetime
import json

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from content.caracteristiques import REGIONS, construire_caracteristiques

CHEMIN_MODELE = "models/modele_consommation.joblib"
CHEMIN_METRIQUES = "models/metriques.json"

# Libellés lisibles des variables du modèle
LIBELLES = {
    "Région": "Région",
    "TMin (°C)": "Température minimale",
    "TMoy (°C)": "Température moyenne",
    "TMax (°C)": "Température maximale",
    "Heure": "Heure",
    "Jour_semaine": "Jour de la semaine",
    "Ferie": "Jour férié",
    "sin_jour_annee": "Saison (sinus du jour de l'année)",
    "cos_jour_annee": "Saison (cosinus du jour de l'année)",
    "Année": "Année",
}


@st.cache_resource
def load_model(filepath=CHEMIN_MODELE):
    """Load and cache the prediction pipeline."""
    return joblib.load(filepath)


@st.cache_data
def load_metrics(filepath=CHEMIN_METRIQUES):
    """Métriques mesurées sur le jeu de test par scripts/entrainer_modele.py."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def format_mw(valeur, signe=False):
    """Nombre en MW avec espace insécable comme séparateur de milliers."""
    texte = f"{valeur:+,.0f}" if signe else f"{valeur:,.0f}"
    return f"{texte} MW".replace(",", "\u202f")


def format_date(texte):
    """2020-11-01 → 01/11/2020."""
    return datetime.date.fromisoformat(texte).strftime("%d/%m/%Y")


def default_date(derniere_annee):
    """Date du jour ramenée à la dernière année vue par le modèle."""
    today = datetime.date.today()
    try:
        return today.replace(year=derniere_annee)
    except ValueError:
        # 29 février d'une année non bissextile
        return today.replace(year=derniere_annee, day=28)


def get_user_input(derniere_annee):
    """
    Collect user input from the Streamlit interface.

    Returns:
        dict: Dictionary of user-provided input data.
    """
    st.subheader("Configuration de la prédiction")
    col1, col2 = st.columns([1, 1])

    with col1:
        region = st.selectbox("Région", REGIONS)
        date = st.date_input("Date", value=default_date(derniere_annee))
        heure = st.time_input(
            "Heure", datetime.time(19, 0), step=datetime.timedelta(minutes=30)
        )

    with col2:
        st.markdown("##### Températures de la journée (°C)")
        tmin = st.number_input("Température minimale", value=5.0, step=0.5)
        tmoy = st.number_input("Température moyenne", value=10.0, step=0.5)
        tmax = st.number_input("Température maximale", value=15.0, step=0.5)

    return {
        "region": region,
        "date": date,
        "heure": heure.hour + heure.minute / 60.0,
        "tmin": tmin,
        "tmoy": tmoy,
        "tmax": tmax,
    }


def show_metrics(metriques):
    """Performances mesurées sur des données que le modèle n'a pas vues."""
    test = metriques["test"]
    reference = metriques["reference_profil_moyen"]
    debut, fin = (format_date(d) for d in metriques["periode_test"])

    st.subheader("Performances sur le jeu de test")
    lignes = f"{metriques['lignes_test']:,}".replace(",", " ")
    st.markdown(
        f"Mesurées sur **{lignes} demi-heures** du {debut} au {fin}, "
        "une période que le modèle n'a pas vue pendant l'apprentissage. Les écarts sous "
        "chaque valeur comparent à une référence naïve : la consommation moyenne observée "
        "pour la même région, le même mois, le même jour de la semaine et la même heure."
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Erreur absolue moyenne (MAE)", format_mw(test["mae"]),
        delta=format_mw(test["mae"] - reference["mae"], signe=True), delta_color="inverse",
    )
    col2.metric(
        "RMSE", format_mw(test["rmse"]),
        delta=format_mw(test["rmse"] - reference["rmse"], signe=True), delta_color="inverse",
    )
    col3.metric(
        "R²", f"{test['r2']:.3f}",
        delta=f"{test['r2'] - reference['r2']:+.3f}",
    )
    col4.metric(
        "Erreur relative moyenne", f"{test['mape']:.1%}",
        delta=f"{(test['mape'] - reference['mape']) * 100:+.1f} pt", delta_color="inverse",
    )

    with st.expander("Détail des performances et poids des variables"):
        par_region = pd.DataFrame(metriques["par_region"]).T.sort_values("mape")
        par_region = pd.DataFrame(
            {
                "MAE (MW)": par_region["mae"].round(0).astype(int),
                "Erreur relative": (par_region["mape"] * 100).round(1).astype(str) + " %",
            }
        )
        st.markdown("**Erreur par région** sur la période de test")
        st.dataframe(par_region, width="stretch")

        importance = (
            pd.Series(metriques["importance_mae_mw"])
            .rename(index=LIBELLES)
            .clip(lower=0)
            .sort_values()
        )
        fig = px.bar(
            importance, orientation="h",
            labels={"value": "Hausse de la MAE si la variable est brouillée (MW)", "index": ""},
        )
        fig.update_layout(showlegend=False, height=380, margin=dict(l=0, r=0, t=10, b=0))
        st.markdown(
            "**Poids des variables** : de combien l'erreur augmente quand on mélange "
            "au hasard les valeurs d'une variable dans le jeu de test (importance par permutation)."
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "L'année pèse zéro sur la période de test : le modèle n'a vu que les années "
            f"{metriques['annees'][0]} à {metriques['annees'][1]} et traite toute année "
            "plus récente comme la dernière connue."
        )


def show_temperature_effect(model, user_input):
    """Consommation prédite selon la température, toutes choses égales par ailleurs."""
    ecart_bas = user_input["tmoy"] - user_input["tmin"]
    ecart_haut = user_input["tmax"] - user_input["tmoy"]
    temperatures = np.arange(-10, 35.5, 0.5)
    X = construire_caracteristiques(
        user_input["region"], [user_input["date"]] * len(temperatures), user_input["heure"],
        temperatures - ecart_bas, temperatures, temperatures + ecart_haut,
    )
    courbe = pd.DataFrame(
        {"Température moyenne (°C)": temperatures, "Consommation prédite (MW)": model.predict(X)}
    )
    fig = px.line(courbe, x="Température moyenne (°C)", y="Consommation prédite (MW)")
    fig.add_vline(x=user_input["tmoy"], line_dash="dot")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.markdown(
        f"**Effet de la température** pour {user_input['region']}, à la même date et à la "
        "même heure (l'écart entre minimale, moyenne et maximale est conservé)."
    )
    st.plotly_chart(fig, width="stretch")


def modelisation():
    """
    Main function to handle the "Modélisation" page.

    It collects user inputs and displays the model prediction and its measured performance.
    """
    model = load_model()
    metriques = load_metrics()
    premiere_annee, derniere_annee = metriques["annees"]

    st.title("🔮 Modélisation et prédictions")
    st.image("images/ML.png", width=300)

    st.markdown(
        f"""
        Cette page permet de **prédire la consommation d'électricité** d'une région (en MW)
        à une date et une heure données, selon les températures de la journée. Le modèle est un
        **gradient boosting** (`HistGradientBoostingRegressor`), entraîné sur les consommations
        par demi-heure et les températures régionales de {premiere_annee} à {derniere_annee}.
        Il tient compte de la région, de la température, de l'heure, du jour de la semaine,
        des jours fériés, de la saison et de l'année.
        """
    )

    st.divider()
    show_metrics(metriques)
    st.divider()

    user_input = get_user_input(derniere_annee)

    if not user_input["tmin"] <= user_input["tmoy"] <= user_input["tmax"]:
        st.warning(
            "La température moyenne devrait se situer entre la minimale et la maximale.",
            icon="⚠️",
        )
    annee = user_input["date"].year
    if not premiere_annee <= annee <= derniere_annee:
        st.warning(
            f"Le modèle a appris sur les années {premiere_annee} à {derniere_annee}. "
            f"Pour {annee}, il applique le niveau de consommation de "
            f"{derniere_annee if annee > derniere_annee else premiere_annee} : "
            "l'évolution d'une année sur l'autre n'est pas extrapolée.",
            icon="⚠️",
        )

    st.divider()

    if st.button("⚡ Prédire la consommation électrique"):
        X = construire_caracteristiques(
            user_input["region"], [user_input["date"]], user_input["heure"],
            user_input["tmin"], user_input["tmoy"], user_input["tmax"],
        )
        prediction = model.predict(X)[0]
        st.success(
            f"🌟 Consommation prédite : **{format_mw(prediction)}** "
            f"(erreur typique sur le jeu de test : ± {metriques['test']['mape']:.0%})",
            icon="🔮",
        )
        show_temperature_effect(model, user_input)
