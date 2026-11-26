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
CHEMIN_TEMPERATURES = "datasets/temp.csv"
COLONNES_TEMPERATURES = ["TMin (°C)", "TMoy (°C)", "TMax (°C)"]

# Jours de part et d'autre de la date choisie, toutes années confondues :
# pour les températures proposées par défaut, et pour la plage de la courbe
FENETRE_NORMALES = 7
FENETRE_PLAGE = 15

# Clés des widgets de la page dans st.session_state
CLE_REGION, CLE_DATE = "modelisation_region", "modelisation_date"
CLES_TEMPERATURES = ["modelisation_tmin", "modelisation_tmoy", "modelisation_tmax"]

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


@st.cache_data
def load_temperatures(filepath=CHEMIN_TEMPERATURES):
    """Températures journalières observées par région (les mêmes qu'à l'entraînement)."""
    temp = pd.read_csv(filepath, sep=";", usecols=["Date", "Région", *COLONNES_TEMPERATURES])
    temp["Date"] = pd.to_datetime(temp["Date"], dayfirst=True)
    temp["Jour_annee"] = temp["Date"].dt.dayofyear
    return temp


def meme_periode(temperatures, region, date, fenetre):
    """Relevés de la région à ± fenetre jours de la même date, toutes années confondues."""
    releves = temperatures[temperatures["Région"] == region]
    ecart = (releves["Jour_annee"] - date.timetuple().tm_yday).abs()
    ecart = np.minimum(ecart, 365 - ecart)  # le 31 décembre est voisin du 1er janvier
    return releves[ecart <= fenetre]


def normales(temperatures, region, date):
    """Températures minimale, moyenne et maximale habituelles, arrondies au demi-degré."""
    periode = meme_periode(temperatures, region, date, FENETRE_NORMALES)
    return [round(periode[colonne].mean() * 2) / 2 for colonne in COLONNES_TEMPERATURES]


def plage_temperatures(temperatures, region, date):
    """Températures moyennes extrêmes observées dans la région à cette période de l'année."""
    tmoy = meme_periode(temperatures, region, date, FENETRE_PLAGE)["TMoy (°C)"]
    return float(tmoy.min()), float(tmoy.max())


def appliquer_normales(temperatures):
    """Remplace les températures saisies par les normales de la région et de la date."""
    valeurs = normales(
        temperatures, st.session_state[CLE_REGION], st.session_state[CLE_DATE]
    )
    for cle, valeur in zip(CLES_TEMPERATURES, valeurs, strict=True):
        st.session_state[cle] = valeur


def format_pct(valeur, decimales=1):
    """0.0551 → 5,5 % (virgule décimale et espace insécable)."""
    return f"{valeur * 100:.{decimales}f}".replace(".", ",") + "\u202f%"


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


def get_user_input(derniere_annee, temperatures):
    """
    Collect user input from the Streamlit interface.

    Les températures proposées sont les normales de la région à la date choisie ;
    elles sont recalculées à chaque changement de région ou de date.

    Returns:
        dict: Dictionary of user-provided input data.
    """
    etat = st.session_state
    etat.setdefault(CLE_REGION, REGIONS[0])
    etat.setdefault(CLE_DATE, default_date(derniere_annee))
    if any(cle not in etat for cle in CLES_TEMPERATURES):
        appliquer_normales(temperatures)

    st.subheader("Configuration de la prédiction")
    col1, col2 = st.columns([1, 1])

    with col1:
        region = st.selectbox(
            "Région", REGIONS, key=CLE_REGION,
            on_change=appliquer_normales, args=(temperatures,),
        )
        date = st.date_input(
            "Date", key=CLE_DATE, on_change=appliquer_normales, args=(temperatures,)
        )
        heure = st.time_input(
            "Heure", datetime.time(19, 0), step=datetime.timedelta(minutes=30)
        )

    with col2:
        st.markdown("##### Températures de la journée (°C)")
        tmin, tmoy, tmax = (
            st.number_input(libelle, step=0.5, format="%.1f", key=cle)
            for libelle, cle in zip(
                ["Température minimale", "Température moyenne", "Température maximale"],
                CLES_TEMPERATURES,
                strict=True,
            )
        )
        debut, fin = temperatures["Date"].dt.year.agg(["min", "max"])
        st.caption(
            f"Proposées par défaut : les normales de la région à cette période de l'année "
            f"(moyenne des relevés de {debut} à {fin}, à ± {FENETRE_NORMALES} jours de la date). "
            "Le modèle prend la météo du jour comme connue : pour une date à venir, "
            "saisir une prévision."
        )

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
        "Erreur relative moyenne (MAPE)", format_pct(test["mape"]),
        delta=f"{(test['mape'] - reference['mape']) * 100:+.1f} pt", delta_color="inverse",
    )

    with st.expander("Détail des performances et poids des variables"):
        par_region = pd.DataFrame(metriques["par_region"]).T.sort_values("mape")
        par_region = pd.DataFrame(
            {
                "MAE (MW)": par_region["mae"].round(0).astype(int),
                "Erreur relative (MAPE)": par_region["mape"].map(format_pct),
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


def show_temperature_effect(model, user_input, temperatures):
    """Consommation prédite selon la température, toutes choses égales par ailleurs."""
    ecart_bas = user_input["tmoy"] - user_input["tmin"]
    ecart_haut = user_input["tmax"] - user_input["tmoy"]
    observe_min, observe_max = plage_temperatures(
        temperatures, user_input["region"], user_input["date"]
    )
    # Plage observée à cette période, élargie de 2 °C et toujours jusqu'à la valeur saisie
    bas = np.floor(min(observe_min, user_input["tmoy"])) - 2
    haut = np.ceil(max(observe_max, user_input["tmoy"])) + 2
    temperatures_courbe = np.arange(bas, haut + 0.25, 0.5)
    X = construire_caracteristiques(
        user_input["region"], [user_input["date"]] * len(temperatures_courbe),
        user_input["heure"],
        temperatures_courbe - ecart_bas, temperatures_courbe, temperatures_courbe + ecart_haut,
    )
    courbe = pd.DataFrame(
        {
            "Température moyenne (°C)": temperatures_courbe,
            "Consommation prédite (MW)": model.predict(X),
        }
    )
    fig = px.line(courbe, x="Température moyenne (°C)", y="Consommation prédite (MW)")
    fig.add_vrect(
        x0=observe_min, x1=observe_max, fillcolor="grey", opacity=0.12, line_width=0,
        annotation_text="observé à cette période", annotation_position="top left",
    )
    fig.add_vline(x=user_input["tmoy"], line_dash="dot")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.markdown(
        f"**Effet de la température** pour {user_input['region']}, à la même date et à la "
        "même heure (l'écart entre minimale, moyenne et maximale est conservé). La zone "
        f"grisée couvre les températures moyennes relevées dans la région à ± {FENETRE_PLAGE} "
        "jours de cette date, toutes années confondues."
    )
    st.plotly_chart(fig, width="stretch")


def modelisation():
    """
    Main function to handle the "Modélisation" page.

    It collects user inputs and displays the model prediction and its measured performance.
    """
    model = load_model()
    metriques = load_metrics()
    temperatures = load_temperatures()
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

    user_input = get_user_input(derniere_annee, temperatures)

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
        mape = metriques["test"]["mape"]
        st.success(
            f"🌟 Consommation prédite : **{format_mw(prediction)}**\n\n"
            f"Sur le jeu de test, les prédictions s'écartent en moyenne de {format_pct(mape)} "
            f"de la consommation réelle (MAPE), soit environ ± {format_mw(prediction * mape)} "
            "à ce niveau. L'écart d'une prédiction isolée peut être plus grand.",
            icon="🔮",
        )
        show_temperature_effect(model, user_input, temperatures)
