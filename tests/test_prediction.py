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
from content.modelisation import (
    CHEMIN_MODELE,
    format_pct,
    load_temperatures,
    normales,
    plage_temperatures,
)
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


def carte_prediction(at):
    """Carte affichée après le clic sur Prédire."""
    cartes = [m for m in at.metric if m.label.startswith("Consommation prédite")]
    assert len(cartes) == 1, "Aucune prédiction affichée"
    return cartes[0]


def lire_mw(at):
    """Valeur en MW de la carte de prédiction."""
    valeur = carte_prediction(at).value
    chiffres = re.fullmatch(r"([\d\u202f]+) MW", valeur)
    assert chiffres, valeur
    return int(chiffres.group(1).replace("\u202f", ""))


def prediction_dans_la_page(tmin, tmoy, tmax):
    at = page_app("modelisation").run()
    sans_exception(at)
    at.selectbox[0].set_value("Île-de-France")
    at.date_input[0].set_value(HIVER).run()  # recalcule les températures par défaut
    at.number_input[0].set_value(tmin)
    at.number_input[1].set_value(tmoy)
    at.number_input[2].set_value(tmax)
    at.button[0].click().run()
    sans_exception(at)
    assert not at.warning, [w.value for w in at.warning]
    # La courbe de l'effet de la température s'affiche avec la prédiction,
    # en plus de la comparaison avec la consommation réelle
    assert len(at.get("plotly_chart")) >= 2
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


# --- Températures par défaut et plage de la courbe ----------------------------

ETE = datetime.date(2020, 7, 15)


@pytest.fixture(scope="module")
def temperatures():
    return load_temperatures.__wrapped__(RACINE / "datasets/temp.csv")


def test_normales_suivent_la_saison_et_la_region(temperatures):
    tmin, tmoy, tmax = normales(temperatures, "Île-de-France", HIVER)
    assert tmin <= tmoy <= tmax
    assert -2 < tmoy < 10, tmoy
    assert normales(temperatures, "Île-de-France", ETE)[1] > tmoy + 10
    # Plus doux en Provence qu'en Grand Est au cœur de l'hiver
    assert (
        normales(temperatures, "Provence-Alpes-Côte d'Azur", HIVER)[1]
        > normales(temperatures, "Grand Est", HIVER)[1] + 3
    )


def test_normales_continues_au_nouvel_an(temperatures):
    """La fenêtre autour du 1er janvier reprend aussi les relevés de fin décembre."""
    premier_janvier = normales(temperatures, "Bretagne", datetime.date(2020, 1, 1))
    trente_et_un = normales(temperatures, "Bretagne", datetime.date(2019, 12, 31))
    assert premier_janvier == pytest.approx(trente_et_un, abs=0.5)


def test_plage_de_la_courbe_selon_la_saison(temperatures):
    bas_hiver, haut_hiver = plage_temperatures(temperatures, "Île-de-France", HIVER)
    bas_ete, haut_ete = plage_temperatures(temperatures, "Île-de-France", ETE)
    assert bas_hiver < 0 < haut_hiver < 20
    assert 10 < bas_ete < haut_ete < 35
    assert haut_hiver < haut_ete


def test_format_pct():
    assert format_pct(0.055135) == "5,5\u202f%"


def test_page_modelisation_propose_les_normales():
    at = page_app("modelisation").run()
    sans_exception(at)
    at.selectbox[0].set_value("Île-de-France")
    at.date_input[0].set_value(HIVER).run()
    hiver = [n.value for n in at.number_input]
    assert hiver[0] <= hiver[1] <= hiver[2]
    at.date_input[0].set_value(ETE).run()
    sans_exception(at)
    assert at.number_input[1].value > hiver[1] + 10
    # Une température saisie à la main est conservée tant que la date ne change pas
    at.number_input[1].set_value(hiver[1]).run()
    at.time_input[0].set_value(datetime.time(8, 0)).run()
    assert at.number_input[1].value == hiver[1]


def test_page_modelisation_libelle_la_mape():
    at = page_app("modelisation").run()
    at.button[0].click().run()
    sans_exception(at)
    carte_prediction(at)
    message = next(c.value for c in at.caption if "MAPE" in c.value)
    assert "MAPE" in message and "± 6" not in message
    assert "5,5\u202f%" in message


def test_page_modelisation_compare_a_la_realite():
    """La semaine de test s'affiche, prédiction proche de la consommation réelle."""
    from content.modelisation import load_metrics, lundis_de_test, semaine_reelle_et_predite

    lundis = lundis_de_test(load_metrics())
    assert len(lundis) >= 50
    semaine = semaine_reelle_et_predite("Île-de-France", lundis[10])
    assert len(semaine) == 7 * 48
    ecart = ((semaine["Prédite"] - semaine["Réelle"]).abs() / semaine["Réelle"]).mean()
    assert ecart < 0.15
