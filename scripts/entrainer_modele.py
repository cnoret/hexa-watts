"""
Réentraîne le modèle de prédiction de la consommation et mesure ses performances.

Données : consommation régionale par demi-heure (datasets/df_modified.parquet)
jointe aux températures journalières régionales (datasets/temp.csv), soit la
période commune du 1er janvier 2016 au 31 octobre 2021.

Découpage temporel : le modèle apprend sur les données jusqu'au 31 octobre 2020
et il est évalué sur les douze mois suivants, qu'il n'a jamais vus. Le modèle
enregistré est exactement celui qui a été évalué, si bien que les métriques
affichées dans l'application sont les siennes.

Usage, depuis la racine du dépôt :
    python scripts/entrainer_modele.py
"""

import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from content.caracteristiques import COLONNES, REGIONS, construire_caracteristiques  # noqa: E402

FIN_APPRENTISSAGE = pd.Timestamp("2020-10-31")
GRAINE = 42


def charger_donnees():
    """Consommation par demi-heure jointe aux températures du jour."""
    conso = pd.read_parquet(
        RACINE / "datasets/df_modified.parquet",
        columns=["Région", "Date", "Heure", "Consommation (MW)"],
    )
    conso["Date"] = pd.to_datetime(conso["Date"])
    heure = conso["Heure"].str.split(":", expand=True).astype(int)
    conso["Heure"] = heure[0] + heure[1] / 60

    temp = pd.read_csv(RACINE / "datasets/temp.csv", sep=";")
    temp["Date"] = pd.to_datetime(temp["Date"], dayfirst=True)
    temp = temp[["Date", "Région", "TMin (°C)", "TMax (°C)", "TMoy (°C)"]]

    donnees = conso.merge(temp, on=["Région", "Date"], how="inner")
    return donnees.sort_values(["Date", "Heure", "Région"], ignore_index=True)


def preparer(donnees):
    """Variables d'entrée (X) et cible (y)."""
    X = construire_caracteristiques(
        donnees["Région"], donnees["Date"], donnees["Heure"],
        donnees["TMin (°C)"], donnees["TMoy (°C)"], donnees["TMax (°C)"],
    )
    return X, donnees["Consommation (MW)"].to_numpy()


def creer_modele():
    """Encodage de la région puis gradient boosting sur histogrammes."""
    encodage = ColumnTransformer(
        [("region", OrdinalEncoder(categories=[REGIONS]), ["Région"])],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )
    regresseur = HistGradientBoostingRegressor(
        max_iter=500,
        learning_rate=0.1,
        max_leaf_nodes=63,
        min_samples_leaf=50,
        l2_regularization=1.0,
        categorical_features=[0],
        early_stopping=False,
        random_state=GRAINE,
    )
    return Pipeline([("encodage", encodage), ("regresseur", regresseur)])


def metriques(y_vrai, y_pred):
    """MAE, RMSE, R² et erreur relative moyenne (MAPE)."""
    return {
        "mae": float(mean_absolute_error(y_vrai, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_vrai, y_pred))),
        "r2": float(r2_score(y_vrai, y_pred)),
        "mape": float(np.mean(np.abs(y_vrai - y_pred) / y_vrai)),
    }


def profil_moyen(X_app, y_app, X_test):
    """Référence naïve : moyenne par région, mois, jour de la semaine et heure."""
    def cle(X):
        mois = pd.to_datetime(
            (np.arctan2(X["sin_jour_annee"], X["cos_jour_annee"]) % (2 * np.pi))
            / (2 * np.pi) * 365.25, unit="D", origin="2001-01-01"
        ).dt.month
        return pd.MultiIndex.from_arrays(
            [X["Région"], mois, X["Jour_semaine"], X["Heure"]]
        )
    moyennes = pd.Series(y_app).groupby(cle(X_app)).mean()
    return moyennes.reindex(cle(X_test)).to_numpy()


def main():
    debut = time.time()
    donnees = charger_donnees()
    X, y = preparer(donnees)
    dates = donnees["Date"]
    apprentissage = (dates <= FIN_APPRENTISSAGE).to_numpy()
    X_app, y_app = X[apprentissage], y[apprentissage]
    X_test, y_test = X[~apprentissage], y[~apprentissage]
    print(f"Apprentissage : {len(X_app):,} lignes, test : {len(X_test):,} lignes")

    modele = creer_modele().fit(X_app, y_app)
    y_pred = modele.predict(X_test)
    resultats = metriques(y_test, y_pred)
    reference = metriques(y_test, profil_moyen(X_app, y_app, X_test))
    print("Modèle :", resultats)
    print("Profil moyen :", reference)

    # Importance par permutation, sur un échantillon du jeu de test
    rng = np.random.default_rng(GRAINE)
    echantillon = rng.choice(len(X_test), size=50_000, replace=False)
    importance = permutation_importance(
        modele, X_test.iloc[echantillon], y_test[echantillon],
        scoring="neg_mean_absolute_error", n_repeats=3, random_state=GRAINE,
    )

    # Erreur par région, pour l'affichage
    erreurs = pd.DataFrame(
        {"Région": X_test["Région"], "abs": np.abs(y_test - y_pred), "y": y_test}
    ).groupby("Région")
    par_region = {
        region: {"mae": float(g["abs"].mean()), "mape": float((g["abs"] / g["y"]).mean())}
        for region, g in erreurs
    }

    joblib.dump(modele, RACINE / "models/modele_consommation.joblib", compress=3)
    rapport = {
        "modele": "HistGradientBoostingRegressor",
        "scikit_learn": sklearn.__version__,
        "variables": COLONNES,
        "periode_apprentissage": [
            str(dates[apprentissage].min().date()), str(FIN_APPRENTISSAGE.date())
        ],
        "periode_test": [
            str(dates[~apprentissage].min().date()), str(dates[~apprentissage].max().date())
        ],
        "lignes_apprentissage": int(len(X_app)),
        "lignes_test": int(len(X_test)),
        "annees": [int(X_app["Année"].min()), int(X_app["Année"].max())],
        "test": resultats,
        "reference_profil_moyen": reference,
        "par_region": par_region,
        "importance_mae_mw": {
            nom: float(valeur)
            for nom, valeur in zip(COLONNES, importance.importances_mean)
        },
    }
    with open(RACINE / "models/metriques.json", "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    print(f"Terminé en {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
