"""
Page « Analyses et visualisations » de l'application Hexa Watts.

Les données sont agrégées une fois (et mises en cache) par année, puis
filtrées selon la période choisie dans la barre latérale. Chaque graphique
est construit par une fonction du module, à partir de ces petites tables.
"""

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyarrow.compute as pc
import pyarrow.parquet as pq
import streamlit as st

from content.caracteristiques import REGIONS
from content.couleurs import COULEURS_EUROPE, COULEURS_FILIERES
from content.interface import (
    a_retenir,
    en_tete,
    graphique,
    indicateurs,
    mettre_en_avant,
    nombre_fr,
)
from content.memoire import liberer_memoire
from content.textes_analyses import DETAILS

# Couleurs des filières (partagées avec la page Préparation)
colors = COULEURS_FILIERES
colors_euro = COULEURS_EUROPE

PREMIERE_ANNEE, DERNIERE_ANNEE = 2013, 2021
# Les échanges physiques de 2021 sont vides ou décalés dans le fichier
DERNIERE_ANNEE_ECHANGES = 2020
CHEMIN_REGIONS = "datasets/regions.geojson"
# 12 régions : la palette par défaut n'a que 10 couleurs
PALETTE_REGIONS = px.colors.qualitative.Dark24

PROD_COLS = [
    "Thermique (MW)",
    "Nucléaire (MW)",
    "Eolien (MW)",
    "Solaire (MW)",
    "Hydraulique (MW)",
    "Bioénergies (MW)",
]
GREEN_COLS = ["Eolien (MW)", "Solaire (MW)", "Hydraulique (MW)", "Bioénergies (MW)"]
# Mêmes filières, sous leur nom après conversion en TWh
GREEN_NAMES = [c.removesuffix(" (MW)") for c in GREEN_COLS]

# Eco2Mix donne une puissance moyenne (MW) par pas d'une demi-heure : l'énergie
# d'un pas vaut donc 0,5 h × puissance, en MWh. 1 TWh = 1 000 000 MWh.
HEURES_PAR_PAS = 0.5
MWH_PAR_TWH = 1_000_000

# Les mois du fichier tco_tch sont en anglais : on les traduit, dans l'ordre
# chronologique pour plotly
MOIS_FR = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre",
}
MONTH_ORDER = list(MOIS_FR.values())

JOURS_FR = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche",
}
JOUR_ORDER = list(JOURS_FR.values())

# Tranches horaires du graphique CF3 : (libellé, heure de début, heure de fin)
PERIODES = [
    ("Nuit (22 h - 6 h)", 22, 6),
    ("Matin (6 h - 9 h)", 6, 9),
    ("Fin de matinée (9 h - 12 h)", 9, 12),
    ("Midi (12 h - 14 h)", 12, 14),
    ("Après-midi (14 h - 17 h)", 14, 17),
    ("Soirée (17 h - 22 h)", 17, 22),
]
NB_REGIONS = 12


def _periode(heure):
    """Tranche horaire d'une heure « HH:MM »."""
    h = int(heure[:2])
    for libelle, debut, fin in PERIODES:
        if (debut <= h < fin) if debut < fin else (h >= debut or h < fin):
            return libelle
    raise ValueError(heure)


def _en_twh(df, columns):
    """
    Convertit des sommes de puissances demi-horaires (MW) en énergie (TWh)
    et retire le suffixe « (MW) » des noms de colonnes.
    """
    df = df.copy()
    df[columns] = df[columns] * HEURES_PAR_PAS / MWH_PAR_TWH
    return df.rename(columns={c: c.removesuffix(" (MW)") for c in columns})


def _aggregate(table, keys, columns, how="sum"):
    """
    Agrège une table Arrow par `keys` et renvoie un petit DataFrame trié.

    Le calcul reste dans Arrow : on évite ainsi de convertir 1,9 million de
    lignes en DataFrame pandas, ce qui doublait le pic de mémoire.
    """
    # min_count=0 : une somme sans valeur vaut 0, comme avec pandas
    options = pc.ScalarAggregateOptions(min_count=0) if how == "sum" else None
    grouped = table.group_by(keys, use_threads=False).aggregate(
        [(column, how, options) for column in columns]
    )
    grouped = grouped.rename_columns(
        [name.removesuffix(f"_{how}") for name in grouped.column_names]
    )
    return (
        grouped.to_pandas()[list(keys) + list(columns)]
        .sort_values(list(keys))
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner="Préparation des données Eco2Mix...")
def load_eco2mix_aggregates(filepath="datasets/df_modified.parquet"):
    """
    Lit uniquement les colonnes utiles du jeu Eco2Mix et renvoie les petites
    tables agrégées dont les graphiques ont besoin, toutes par année pour
    pouvoir filtrer la période ensuite.

    Le jeu complet (1,9 million de lignes, environ 550 Mo en mémoire) n'est
    jamais conservé : seul le résultat agrégé, de quelques milliers de lignes
    au plus, est mis en cache.
    """
    columns = [
        "Région",
        "Année",
        "Mois",
        "Jour",
        "Heure",
        "Consommation (MW)",
        "Production (MW)",
        "Ech. physiques (MW)",
    ] + PROD_COLS
    table = pq.read_table(filepath, columns=columns)

    # Les sommes de MW sont converties en TWh (voir HEURES_PAR_PAS)

    # Production par année et par filière (PF1, PF2, indicateurs)
    prod_yearly = _en_twh(
        _aggregate(table, ["Année"], PROD_COLS), PROD_COLS
    ).set_index("Année")

    # Production par région, par année et par filière (PF3, PF4, PF6)
    prod_region = _en_twh(_aggregate(table, ["Région", "Année"], PROD_COLS), PROD_COLS)

    # Solde des échanges physiques par région et par année (DF1, carte), sans 2021
    distrib = _en_twh(
        _aggregate(table, ["Région", "Année"], ["Ech. physiques (MW)"]),
        ["Ech. physiques (MW)"],
    )
    distrib = distrib[distrib["Année"] <= DERNIERE_ANNEE_ECHANGES].reset_index(drop=True)

    # Journée type par année (CF4)
    df_daily = _aggregate(table, ["Heure", "Année"], ["Consommation (MW)"], "mean")

    # Consommation par région et par année (CF1)
    cons_yearly = _en_twh(
        _aggregate(table, ["Région", "Année"], ["Consommation (MW)"]),
        ["Consommation (MW)"],
    )

    # Consommation par mois et par année (CF2)
    cons_monthly = _en_twh(
        _aggregate(table, ["Mois", "Année"], ["Consommation (MW)"]), ["Consommation (MW)"]
    )
    cons_monthly["Mois"] = pd.Categorical(
        cons_monthly["Mois"].map(MOIS_FR), categories=MONTH_ORDER, ordered=True
    )

    # Puissance moyenne appelée en France par jour, tranche horaire et année (CF3).
    # Chaque demi-heure compte une ligne par région : la moyenne d'une ligne
    # multipliée par le nombre de régions donne la consommation nationale.
    weekly = _aggregate(table, ["Jour", "Heure", "Année"], ["Consommation (MW)"], "mean")
    weekly["Période"] = weekly["Heure"].map(_periode)
    weekly = (
        weekly.groupby(["Jour", "Période", "Année"])["Consommation (MW)"].mean()
        * NB_REGIONS / 1000
    ).rename("Consommation (GW)").reset_index()
    weekly["Jour"] = pd.Categorical(
        weekly["Jour"].map(JOURS_FR), categories=JOUR_ORDER, ordered=True
    )
    weekly["Période"] = pd.Categorical(
        weekly["Période"], categories=[p[0] for p in PERIODES], ordered=True
    )

    # Production et consommation par région et par année (PCF1)
    consprod = _en_twh(
        _aggregate(table, ["Région", "Année"], ["Consommation (MW)", "Production (MW)"]),
        ["Consommation (MW)", "Production (MW)"],
    )

    del table
    liberer_memoire()

    return {
        "prod_yearly": prod_yearly,
        "prod_region": prod_region,
        "distrib": distrib,
        "df_daily": df_daily,
        "consprod": consprod,
        "cons_yearly": cons_yearly,
        "cons_monthly": cons_monthly,
        "weekly": weekly,
    }


@st.cache_data(show_spinner="Préparation des taux de charge...")
def load_tco_tch_aggregates(filepath="datasets/tco_tch.parquet"):
    """Moyennes mensuelles par région et par année des taux de charge et de couverture."""
    measures = ["TCH Solaire (%)", "TCH Eolien (%)", "TCO Nucléaire (%)"]
    tco_tch = pq.read_table(filepath, columns=["Date", "Région", "Mois"] + measures).to_pandas()
    tco_tch["Année"] = pd.to_datetime(tco_tch.pop("Date")).dt.year
    grouped = tco_tch.groupby(["Région", "Année", "Mois"])[measures].mean().reset_index()
    grouped["Mois"] = pd.Categorical(
        grouped["Mois"].map(MOIS_FR), categories=MONTH_ORDER, ordered=True
    )
    del tco_tch
    liberer_memoire()
    return grouped


@st.cache_data
def load_europe_data(filepath="datasets/EUROPE_DATA.csv"):
    """
    Données Eurostat (petit fichier CSV).

    Malgré son nom, la colonne « Valeur (MW) » contient des énergies annuelles
    en MWh (l'hydraulique de la France en 2020 y vaut 62,6 millions, soit
    62,6 TWh) : on la convertit en TWh.
    """
    europe = pd.read_csv(filepath, sep=",")
    europe["Énergie (TWh)"] = europe.pop("Valeur (MW)") / MWH_PAR_TWH
    return europe


@st.cache_data
def load_regions(filepath=CHEMIN_REGIONS):
    """Contours simplifiés des régions métropolitaines (GeoJSON de Grégoire David)."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


# --- Filtres -----------------------------------------------------------------


def filtrer(df, debut, fin, colonne="Année"):
    """Lignes dont l'année est comprise entre debut et fin (incluses)."""
    annees = df.index if colonne is None else df[colonne]
    return df[(annees >= debut) & (annees <= fin)]


def libelle_periode(debut, fin):
    """« en 2018 » ou « de 2013 à 2021 »."""
    return f"en {debut}" if debut == fin else f"de {debut} à {fin}"


def filtres():
    """Filtres de la barre latérale : période et région mise en avant."""
    with st.sidebar:
        st.markdown("**Filtres**")
        debut, fin = st.slider(
            "Période",
            min_value=PREMIERE_ANNEE,
            max_value=DERNIERE_ANNEE,
            value=(PREMIERE_ANNEE, DERNIERE_ANNEE),
            key="analyses_periode",
        )
        choix = st.selectbox(
            "Région mise en avant",
            ["Aucune"] + REGIONS,
            key="analyses_region",
            help="Les autres régions passent en gris dans les graphiques par région.",
        )
    return debut, fin, None if choix == "Aucune" else choix


def _indicateurs_cles(prod_yearly, cons_yearly):
    """Indicateurs clés de la période choisie : dernière année comparée à la première."""
    premiere, derniere = prod_yearly.index.min(), prod_yearly.index.max()
    total = prod_yearly.sum(axis=1)
    part_nucleaire = prod_yearly["Nucléaire"] / total * 100
    part_verte = prod_yearly[GREEN_NAMES].sum(axis=1) / total * 100
    conso = cons_yearly.groupby("Année")["Consommation"].sum()

    def ecart(serie):
        if premiere == derniere:
            return None
        return f"{nombre_fr(serie[derniere] - serie[premiere], 1, signe=True)} pts depuis {premiere}"

    def rappel(serie):
        if premiere == derniere:
            return None
        return f"{nombre_fr(serie[premiere])} TWh en {premiere}"

    indicateurs(
        [
            (f"Production {derniere}", f"{nombre_fr(total[derniere])} TWh", rappel(total)),
            (f"Consommation {derniere}", f"{nombre_fr(conso[derniere])} TWh", rappel(conso)),
            (f"Part du nucléaire {derniere}", f"{nombre_fr(part_nucleaire[derniere], 1)} %",
             ecart(part_nucleaire)),
            (f"Part renouvelable {derniere}", f"{nombre_fr(part_verte[derniere], 1)} %",
             ecart(part_verte)),
        ]
    )


# --- Graphiques : production --------------------------------------------------


def _hauteur_barres(n):
    """Hauteur d'un graphique en barres horizontales de n catégories."""
    return max(360, 140 + 26 * n)


def graphique_mix(prod, periode):
    """PF1 : part de chaque filière dans la production annuelle."""
    part = prod.divide(prod.sum(axis=1), axis=0) * 100
    part_nucleaire = prod["Nucléaire"].sum() / prod.to_numpy().sum() * 100
    fig = go.Figure(
        [
            go.Bar(x=part.index, y=part[filiere], name=filiere,
                   marker_color=colors[filiere],
                   hovertemplate="%{x} : %{y:.1f} %<extra>" + filiere + "</extra>")
            for filiere in part.columns
        ]
    )
    fig.update_layout(
        barmode="stack",
        title=f"Le nucléaire fournit {nombre_fr(part_nucleaire)} % de l'électricité produite {periode}",
        xaxis=dict(title="Année", dtick=1),
        yaxis_title="Part de la production (%)",
    )
    return fig


def graphique_renouvelables(prod, periode):
    """PF2 : production renouvelable par année et par filière."""
    verte = prod[GREEN_NAMES]
    total = verte.sum(axis=1)
    if len(total) > 1:
        titre = (
            f"La production renouvelable passe de {nombre_fr(total.iloc[0])} TWh "
            f"en {total.index[0]} à {nombre_fr(total.iloc[-1])} TWh en {total.index[-1]}"
        )
    else:
        titre = f"Production renouvelable : {nombre_fr(total.iloc[0])} TWh {periode}"
    fig = px.bar(
        verte.reset_index(),
        x="Année",
        y=GREEN_NAMES,
        title=titre,
        labels={"value": "Production (TWh)", "variable": "Filière"},
        color_discrete_map=colors,
    )
    fig.update_layout(barmode="stack", xaxis_dtick=1)
    return fig


def graphique_renouvelables_regions(prod_region, periode, region):
    """PF3 : production renouvelable cumulée par région, en barres horizontales triées."""
    verte = prod_region.groupby("Région")[GREEN_NAMES].sum()
    verte = verte.loc[verte.sum(axis=1).sort_values().index]
    premiere = verte.index[-1]
    fig = px.bar(
        verte.reset_index(),
        y="Région",
        x=GREEN_NAMES,
        orientation="h",
        title=f"Production renouvelable par région {periode} : {premiere} en tête",
        labels={"value": "Production cumulée (TWh)", "variable": "Filière", "Région": ""},
        color_discrete_map=colors,
        height=_hauteur_barres(len(verte)),
    )
    fig.update_layout(barmode="stack")
    return mettre_en_avant(fig, region)


def graphique_filiere_regions(prod_region, filiere, periode):
    """PF4 : répartition d'une filière renouvelable entre les régions."""
    parts = prod_region.groupby("Région")[filiere].sum().reset_index()
    fig = px.pie(
        parts,
        names="Région",
        values=filiere,
        # Du vert foncé au vert moyen : les verts très clairs ne se voient pas sur fond blanc
        color_discrete_sequence=px.colors.sample_colorscale(
            "Greens", [1 - i / 16 for i in range(12)]
        ),
        title=f"Répartition de la production {filiere.lower()} par région, {periode}",
    )
    return fig


def graphique_nucleaire_regions(prod_region, periode, region):
    """PF6 : production nucléaire cumulée des régions qui ont des centrales."""
    nucleaire = prod_region.groupby("Région")["Nucléaire"].sum()
    nucleaire = nucleaire[nucleaire > 0].sort_values()
    fig = px.bar(
        nucleaire.reset_index(),
        y="Région",
        x="Nucléaire",
        orientation="h",
        title=f"Seules {len(nucleaire)} régions produisent de l'électricité nucléaire",
        labels={"Nucléaire": f"Production cumulée {periode} (TWh)", "Région": ""},
        color_discrete_sequence=[colors["Nucléaire"]],
        height=_hauteur_barres(len(nucleaire)),
    )
    return mettre_en_avant(fig, region)


# --- Graphiques : taux de charge et de couverture -----------------------------


def graphique_taux(tco_tch, mesure, titre, region):
    """TCF1 à TCF3 : moyenne mensuelle d'un taux, par région."""
    moyennes = tco_tch.groupby(["Région", "Mois"], observed=True)[mesure].mean().reset_index()
    fig = px.line(
        moyennes.sort_values("Mois"),
        x="Mois",
        y=mesure,
        color="Région",
        title=titre,
        labels={mesure: f"{mesure.split(' (')[0]} moyen (%)", "Mois": ""},
        color_discrete_sequence=PALETTE_REGIONS,
        category_orders={"Région": REGIONS},
    )
    return mettre_en_avant(fig, region)


# --- Graphiques : consommation ------------------------------------------------


def graphique_conso_regions(cons_yearly, region):
    """CF1 : consommation annuelle par région."""
    ordre = cons_yearly.groupby("Région")["Consommation"].sum().sort_values(ascending=False)
    fig = px.line(
        cons_yearly,
        x="Année",
        y="Consommation",
        color="Région",
        markers=True,
        title=f"Consommation annuelle par région : {ordre.index[0]} en tête",
        labels={"Consommation": "Consommation (TWh)"},
        color_discrete_sequence=PALETTE_REGIONS,
        category_orders={"Région": ordre.index.tolist()},
    )
    fig.update_layout(height=520, xaxis_dtick=1)
    return mettre_en_avant(fig, region)


def graphique_conso_mois(cons_monthly, periode):
    """CF2 : consommation moyenne de chaque mois sur la période."""
    par_mois = (
        cons_monthly.groupby("Mois", observed=True)["Consommation"].mean().reset_index()
    )
    haut = par_mois.loc[par_mois["Consommation"].idxmax()]
    bas = par_mois.loc[par_mois["Consommation"].idxmin()]
    ratio = haut["Consommation"] / bas["Consommation"]
    fig = px.bar(
        par_mois,
        x="Mois",
        y="Consommation",
        title=(
            f"En {haut['Mois'].lower()}, la France consomme {nombre_fr(ratio, 1)} fois "
            f"plus qu'en {bas['Mois'].lower()} (moyenne {periode})"
        ),
        labels={"Consommation": "Consommation moyenne (TWh)", "Mois": ""},
        color="Consommation",
        color_continuous_scale=[[0, "#BFD3F2"], [1, "#2E5EAA"]],
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


def graphique_conso_semaine(weekly):
    """CF3 : puissance appelée selon le jour et la tranche horaire."""
    moyenne = (
        weekly.groupby(["Période", "Jour"], observed=True)["Consommation (GW)"]
        .mean()
        .reset_index()
    )
    fig = px.line(
        moyenne,
        x="Jour",
        y="Consommation (GW)",
        color="Période",
        markers=True,
        title="La consommation baisse le week-end, surtout le dimanche",
        labels={"Jour": "", "Consommation (GW)": "Puissance moyenne appelée (GW)"},
    )
    return fig


def graphique_journee(df_daily):
    """CF4 : profil moyen d'une journée, par année."""
    fig = px.line(
        df_daily,
        x="Heure",
        y="Consommation (MW)",
        color="Année",
        title="Profil d'une journée type : un creux la nuit, deux pointes à midi et le soir",
        labels={"Consommation (MW)": "Consommation moyenne par région (MW)", "Heure": ""},
    )
    fig.update_xaxes(dtick=4)
    return fig


def graphique_production_conso(consprod, periode, region):
    """PCF1 : production et consommation cumulées par région, avec la diagonale."""
    cumul = consprod.groupby("Région")[["Production", "Consommation"]].sum().reset_index()
    borne = float(cumul[["Production", "Consommation"]].to_numpy().max()) * 1.05
    fig = px.scatter(
        cumul,
        x="Production",
        y="Consommation",
        color="Région",
        size="Production",
        size_max=30,
        title=f"Production et consommation par région, cumulées {periode}",
        labels={"Production": "Production (TWh)", "Consommation": "Consommation (TWh)"},
        color_discrete_sequence=PALETTE_REGIONS,
    )
    fig.add_trace(
        go.Scatter(
            x=[0, borne], y=[0, borne], mode="lines", name="Production = consommation",
            line=dict(color="#94A0B4", dash="dot", width=1), hoverinfo="skip",
        )
    )
    fig.update_layout(height=520)
    return mettre_en_avant(fig, region)


# --- Graphiques : échanges ----------------------------------------------------


def graphique_solde_region(distrib, region):
    """DF1 : solde annuel des échanges physiques d'une région."""
    # Solde annuel en TWh : positif = importations nettes,
    # négatif = exportations nettes vers les autres régions et pays.
    # Points en rouge (importatrice) ou bleu (exportatrice), comme sur la carte.
    region_data = distrib[distrib["Région"] == region]
    solde = region_data["Ech. physiques"]
    fig = go.Figure(
        go.Scatter(
            x=region_data["Année"],
            y=solde,
            mode="lines+markers",
            line=dict(color="#94A0B4"),
            marker=dict(
                size=10,
                color=["#E4572E" if v > 0 else "#2E5EAA" for v in solde],
            ),
            hovertemplate="%{x} : %{y:.1f} TWh<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#94A0B4", line_width=1)
    fig.update_layout(
        title=f"Solde annuel des échanges physiques : {region}",
        xaxis_title="Année",
        yaxis_title="Solde des échanges (TWh)<br>< 0 : exportatrice   > 0 : importatrice",
        xaxis=dict(dtick=1),
        height=460,
    )
    return fig


def _contours(region_geo):
    """Coordonnées x/y d'une région, polygones séparés par None (pour fill='toself')."""
    geometrie = region_geo["geometry"]
    polygones = (
        [geometrie["coordinates"]]
        if geometrie["type"] == "Polygon"
        else geometrie["coordinates"]
    )
    xs, ys = [], []
    for polygone in polygones:
        contour = polygone[0]  # contour extérieur, sans les trous
        xs += [point[0] for point in contour] + [None]
        ys += [point[1] for point in contour] + [None]
    return xs, ys


def carte_echanges(distrib, regions, annee):
    """
    Carte du solde des échanges par région pour une année.

    Les régions sont dessinées comme des polygones remplis sur des axes
    simples : contrairement aux cartes « geo » de Plotly, aucun fond de carte
    n'est téléchargé depuis un serveur extérieur.
    """
    soldes = distrib[distrib["Année"] == annee].set_index("Région")["Ech. physiques"]
    borne = float(distrib["Ech. physiques"].abs().max())
    echelle = px.colors.get_colorscale("RdBu_r")

    def couleur(valeur):
        return px.colors.sample_colorscale(echelle, [(valeur + borne) / (2 * borne)])[0]

    fig = go.Figure()
    for region_geo in regions["features"]:
        nom = region_geo["properties"]["nom"]
        if nom not in soldes:
            continue
        solde = soldes[nom]
        xs, ys = _contours(region_geo)
        sens = "importatrice" if solde > 0 else "exportatrice"
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, fill="toself", mode="lines", name=nom,
                fillcolor=couleur(solde), line=dict(color="white", width=1),
                hoveron="fills",
                text=f"{nom} : {nombre_fr(solde, 1, signe=True)} TWh ({sens})",
                hoverinfo="text", showlegend=False,
            )
        )
    # Trace invisible qui porte l'échelle de couleurs
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(
                colorscale=echelle, cmin=-borne, cmax=borne, color=[0],
                colorbar=dict(title="Solde (TWh)", thickness=12),
            ),
        )
    )
    fig.update_xaxes(visible=False)
    # Un degré de longitude vaut environ 0,69 degré de latitude en France
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1.45)
    fig.update_layout(
        title=f"Régions importatrices en rouge, exportatrices en bleu ({annee})",
        height=600,
        margin=dict(l=0, r=0, b=0),
    )
    return fig


# --- Graphiques : Europe ------------------------------------------------------


def _barres_pays(df, mesure, titre):
    """Énergie cumulée par pays et par type, en barres horizontales triées."""
    par_type = df.groupby(["Pays", "Class"])["Énergie (TWh)"].sum().reset_index()
    ordre = par_type.groupby("Pays")["Énergie (TWh)"].sum().sort_values()
    fig = px.bar(
        par_type,
        y="Pays",
        x="Énergie (TWh)",
        color="Class",
        orientation="h",
        title=titre.format(premier=ordre.index[-1]),
        labels={"Énergie (TWh)": f"{mesure} cumulée (TWh)", "Pays": "", "Class": "Type"},
        category_orders={"Pays": ordre.index.tolist()[::-1]},
        color_discrete_map=colors_euro,
        height=_hauteur_barres(len(ordre)),
    )
    return fig


def _barres_annees(df, mesure, titre):
    """Énergie européenne par année et par type."""
    par_annee = df.groupby(["Année", "Class"])["Énergie (TWh)"].sum().reset_index()
    total = par_annee.groupby("Année")["Énergie (TWh)"].sum()
    fig = px.bar(
        par_annee,
        x="Année",
        y="Énergie (TWh)",
        color="Class",
        title=titre.format(debut=nombre_fr(total.iloc[0]), fin=nombre_fr(total.iloc[-1]),
                           annee_debut=total.index[0], annee_fin=total.index[-1]),
        labels={"Énergie (TWh)": f"{mesure} (TWh)", "Class": "Type"},
        color_discrete_map=colors_euro,
    )
    fig.update_layout(barmode="stack", xaxis_dtick=1)
    return fig


# --- Page ---------------------------------------------------------------------


def visualisation():
    """Contenu de la page Analyses et visualisations."""
    aggregates = load_eco2mix_aggregates()
    tco_tch = load_tco_tch_aggregates()
    europe = load_europe_data()
    debut, fin, region = filtres()
    periode = libelle_periode(debut, fin)

    en_tete(
        "Analyses et visualisations",
        surtitre="Eco2Mix · Eurostat · 2013 – 2021",
        sous_titre="Ce que la France produit, ce qu'elle consomme, et comment "
        "l'électricité circule entre les régions et en Europe.",
    )

    prod_yearly = filtrer(aggregates["prod_yearly"], debut, fin, colonne=None)
    prod_region = filtrer(aggregates["prod_region"], debut, fin)
    cons_yearly = filtrer(aggregates["cons_yearly"], debut, fin)
    _indicateurs_cles(prod_yearly, cons_yearly)
    if (debut, fin) != (PREMIERE_ANNEE, DERNIERE_ANNEE):
        st.caption(
            f"Graphiques et indicateurs filtrés {periode}. Les encadrés « À retenir » "
            f"commentent toute la période {PREMIERE_ANNEE}-{DERNIERE_ANNEE}."
        )

    onglet_prod, onglet_taux, onglet_cons, onglet_echanges, onglet_europe = st.tabs(
        ["Production", "Taux de charge", "Consommation", "Échanges régionaux", "Europe"]
    )

    with onglet_prod:
        graphique(graphique_mix(prod_yearly, periode))
        a_retenir(
            [
                "Le nucléaire assure entre 67 % et 77 % de la production selon les années.",
                "La France a misé sur une électricité pilotable et peu carbonée : "
                "l'onglet Europe la compare à ses voisins.",
            ],
            DETAILS["pf1"],
        )

        graphique(graphique_renouvelables(prod_yearly, periode))
        a_retenir(
            [
                "L'éolien passe de 16 TWh en 2013 à 40 TWh en 2020, le solaire de 4,5 à 14 TWh.",
                "L'hydraulique reste la première source renouvelable : 53 à 75 TWh par an "
                "selon la pluviométrie.",
            ],
            DETAILS["pf2"],
        )

        graphique(graphique_renouvelables_regions(prod_region, periode, region))
        a_retenir(
            [
                "Auvergne-Rhône-Alpes domine nettement (environ 280 TWh), grâce à l'hydraulique.",
                "Le Grand Est et les Hauts-de-France assurent près de la moitié de l'éolien ; "
                "le sud, près des deux tiers du solaire.",
            ],
            DETAILS["pf3"],
        )

        filiere = st.selectbox("Filière renouvelable", GREEN_NAMES)
        graphique(graphique_filiere_regions(prod_region, filiere, periode))

        graphique(graphique_nucleaire_regions(prod_region, periode, region))
        a_retenir(
            [
                "Auvergne-Rhône-Alpes, le Grand Est et le Centre-Val de Loire produisent "
                "chacune 650 à 750 TWh sur la période.",
                "Les régions sans centrale dépendent des échanges : voir l'onglet "
                "Échanges régionaux.",
            ],
            DETAILS["pf6"],
        )
        with st.expander("Pourquoi pas d'éolien en mer ?"):
            st.markdown(DETAILS["pf5"])

    with onglet_taux:
        tco_tch_periode = filtrer(tco_tch, debut, fin)
        st.caption(
            "Le **taux de charge** (TCH) d'une filière rapporte sa production à sa "
            "capacité installée. Le **taux de couverture** (TCO) rapporte la production "
            "d'une filière à la consommation de la région."
        )
        graphique(graphique_taux(
            tco_tch_periode, "TCH Solaire (%)",
            "Le solaire produit le plus en été, sans dépasser la moitié de sa capacité",
            region,
        ))
        a_retenir(
            [
                "Le taux de charge solaire culmine en juillet, autour de 50 % au mieux.",
                "Les régions les plus équipées n'ont pas les meilleurs taux : le Centre-Val "
                "de Loire, 3 % de la production solaire, détient le record.",
            ],
            DETAILS["tcf1"],
        )
        graphique(graphique_taux(
            tco_tch_periode, "TCH Eolien (%)",
            "L'éolien produit le plus en hiver, avec un pic en février",
            region,
        ))
        a_retenir(
            [
                "Le Grand Est et le Centre-Val de Loire dépassent 50 % en février.",
                "Les Hauts-de-France, premiers producteurs (26 % de l'éolien), plafonnent "
                "autour de 49 %.",
            ],
            DETAILS["tcf2"],
        )
        graphique(graphique_taux(
            tco_tch_periode, "TCO Nucléaire (%)",
            "Le Centre-Val de Loire produit bien plus de nucléaire qu'il ne consomme",
            region,
        ))
        a_retenir(
            [
                "Région très productrice et peu consommatrice, le Centre-Val de Loire "
                "dépasse largement 100 % de couverture.",
                "L'écart se creuse quand la consommation baisse, au printemps et en été.",
            ],
            DETAILS["tcf3"],
        )

    with onglet_cons:
        graphique(graphique_conso_regions(cons_yearly, region))
        graphique(graphique_conso_mois(filtrer(aggregates["cons_monthly"], debut, fin), periode))
        graphique(graphique_conso_semaine(filtrer(aggregates["weekly"], debut, fin)))
        graphique(graphique_journee(filtrer(aggregates["df_daily"], debut, fin)))
        graphique(graphique_production_conso(
            filtrer(aggregates["consprod"], debut, fin), periode, region
        ))
        a_retenir(
            [
                "Les régions au-dessus de la diagonale consomment plus qu'elles ne produisent.",
                "Le Centre-Val de Loire produit environ quatre fois sa consommation ; "
                "l'Île-de-France, première consommatrice, à peine 5 %.",
            ],
            DETAILS["pcf1"],
        )

    with onglet_echanges:
        distrib = filtrer(
            aggregates["distrib"], debut, min(fin, DERNIERE_ANNEE_ECHANGES)
        )
        if distrib.empty:
            st.info(
                "Les échanges de 2021 ne sont pas exploitables dans notre jeu de données : "
                "choisissez une période qui commence avant 2021.",
                icon=":material/info:",
            )
        else:
            annees = sorted(distrib["Année"].unique())
            annee = st.select_slider(
                "Année de la carte", options=annees, value=annees[0], key="analyses_annee_carte"
            )
            graphique(carte_echanges(distrib, load_regions(), annee))
            a_retenir(
                [
                    "Cinq des sept régions nucléaires sont exportatrices nettes chaque année "
                    "de 2013 à 2020.",
                    "La Normandie exporte deux fois moins en 2020 qu'en 2013 ; les "
                    "Hauts-de-France deviennent exportateurs en 2018.",
                ],
                DETAILS["df1"],
            )
            choix = st.selectbox(
                "Région", REGIONS, index=REGIONS.index(region) if region else 0
            )
            graphique(graphique_solde_region(distrib, choix))

    with onglet_europe:
        europe = filtrer(europe, debut, fin)
        production = europe[europe["Type"] == "Production"]
        consommation = europe[europe["Type"] == "Consommation"]
        st.caption(
            "Données Eurostat : toutes les formes d'énergie renouvelable, pas seulement "
            "l'électricité."
        )
        graphique(_barres_pays(
            production, "Production",
            "Production d'énergie renouvelable par pays " + periode + " : {premier} en tête",
        ))
        a_retenir(
            [
                "L'Allemagne est en tête (environ 9 900 TWh), devant la France et l'Italie "
                "(environ 5 700 et 5 600 TWh).",
                "La Suède mise sur l'hydroélectricité et la bioénergie.",
            ],
            DETAILS["pe1a"],
        )
        graphique(_barres_annees(
            production, "Production",
            "La production renouvelable européenne passe de {debut} TWh en {annee_debut} "
            "à {fin} TWh en {annee_fin}",
        ))
        a_retenir(
            [
                "La hausse vient surtout des biocarburants (+585 TWh), de la bioénergie "
                "(+208 TWh) et de l'éolien (+177 TWh).",
                "Les pompes à chaleur triplent, le solaire photovoltaïque double ; "
                "l'hydraulique recule légèrement.",
            ],
            DETAILS["pe2a"],
        )
        graphique(_barres_annees(
            consommation, "Consommation",
            "La consommation renouvelable européenne passe de {debut} TWh en {annee_debut} "
            "à {fin} TWh en {annee_fin}",
        ))
        graphique(_barres_pays(
            consommation, "Consommation",
            "Consommation d'énergie renouvelable par pays " + periode + " : {premier} en tête",
        ))
        a_retenir(
            [
                "La consommation d'énergies renouvelables progresse dans toute l'Europe.",
                "Biocarburants et bioénergie en forment la plus grosse part.",
            ],
            DETAILS["ce3"],
        )
