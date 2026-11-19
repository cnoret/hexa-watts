"""La prédiction fonctionne et réagit à la température."""

import datetime
import re

import joblib
import numpy as np
import pytest

from content.caracteristiques import (
    COLONNES,
    REGIONS,
    construire_caracteristiques,
    jours_feries,
)
from content.modelisation import CHEMIN_MODELE
from tests.conftest import RACINE, page_app, sans_exception

HIVER = datetime.date(2020, 1, 15)  # un mercredi


@pytest.fixture(scope="module")
def modele():
    return joblib.load(RACINE / CHEMIN_MODELE)


def predire(modele, tmoy, region="Île-de-France", date=HIVER, heure=19.0):
    X = construire_caracteristiques(region, [date], heure, tmoy - 4, tmoy, tmoy + 4)
    return float(modele.predict(X)[0])


# --- Variables d'entrée -------------------------------------------------------


def test_colonnes_dans_l_ordre_du_modele(modele):
    X = construire_caracteristiques("Bretagne", [HIVER], 12.5, 2.0, 6.0, 10.0)
    assert list(X.columns) == COLONNES
    assert list(modele.feature_names_in_) == COLONNES
    assert len(X) == 1


def test_jours_feries():
    feries = jours_feries(2020)
    assert datetime.date(2020, 4, 13) in feries  # lundi de Pâques
    assert datetime.date(2020, 5, 21) in feries  # Ascension
    assert datetime.date(2020, 6, 1) in feries  # lundi de Pentecôte
    assert datetime.date(2020, 7, 14) in feries
    assert len(feries) == 11
    X = construire_caracteristiques("Bretagne", ["2020-07-14", "2020-07-15"], 12, 15, 20, 25)
    assert X["Ferie"].tolist() == [1, 0]


def test_saison_continue_au_nouvel_an():
    X = construire_caracteristiques("Bretagne", ["2019-12-31", "2020-01-01"], 0, 0, 5, 10)
    assert np.allclose(X["cos_jour_annee"], 1, atol=1e-3)


# --- Modèle -------------------------------------------------------------------


@pytest.mark.parametrize("region", REGIONS)
def test_prediction_plausible_pour_chaque_region(modele, region):
    prediction = predire(modele, 8.0, region=region)
    assert np.isfinite(prediction)
    assert 500 < prediction < 25_000, f"{region} : {prediction:.0f} MW"


def test_plus_froid_consomme_plus(modele):
    """En hiver, une journée froide demande plus d'électricité qu'une journée douce."""
    froid, doux = predire(modele, -5.0), predire(modele, 12.0)
    assert froid > doux * 1.05, f"-5 °C : {froid:.0f} MW, 12 °C : {doux:.0f} MW"


def test_courbe_de_chauffage_decroissante(modele):
    """Entre -10 et 15 °C, la consommation baisse globalement quand la température monte."""
    temperatures = np.arange(-10, 15.5, 0.5)
    X = construire_caracteristiques(
        "Île-de-France", [HIVER] * len(temperatures), 19.0,
        temperatures - 4, temperatures, temperatures + 4,
    )
    courbe = modele.predict(X)
    assert np.corrcoef(temperatures, courbe)[0, 1] < -0.9


# --- Page Modélisation --------------------------------------------------------


def lire_mw(at):
    """Valeur en MW du message de succès affiché après le clic sur Prédire."""
    assert len(at.success) == 1, "Aucune prédiction affichée"
    chiffres = re.search(r"\*\*([\d ]+) MW\*\*", at.success[0].value)
    assert chiffres, at.success[0].value
    return int(chiffres.group(1).replace(" ", ""))


def prediction_dans_la_page(tmin, tmoy, tmax):
    at = page_app("modelisation").run()
    sans_exception(at)
    at.selectbox[0].set_value("Île-de-France")
    at.date_input[0].set_value(HIVER)
    at.number_input[0].set_value(tmin)
    at.number_input[1].set_value(tmoy)
    at.number_input[2].set_value(tmax)
    at.button[0].click().run()
    sans_exception(at)
    assert not at.warning, [w.value for w in at.warning]
    # La courbe de l'effet de la température s'affiche avec la prédiction
    assert at.get("plotly_chart")
    return lire_mw(at)


def test_page_modelisation_predit_et_reagit_a_la_temperature():
    froid = prediction_dans_la_page(-9.0, -5.0, -1.0)
    doux = prediction_dans_la_page(8.0, 12.0, 16.0)
    assert froid > doux, f"froid : {froid} MW, doux : {doux} MW"


def test_page_modelisation_signale_temperatures_incoherentes():
    at = page_app("modelisation").run()
    at.number_input[1].set_value(30.0).run()  # moyenne > maximale
    sans_exception(at)
    assert any("entre la minimale et la maximale" in w.value for w in at.warning)
