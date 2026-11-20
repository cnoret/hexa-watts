"""
Creation of the "Visualisation" page for the Hexa Watts application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pyarrow.compute as pc
import pyarrow.parquet as pq

from content.couleurs import COULEURS_EUROPE, COULEURS_FILIERES
from content.memoire import liberer_memoire


# Couleurs des filières (partagées avec la page Préparation)
colors = COULEURS_FILIERES
colors_euro = COULEURS_EUROPE

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
    tables agrégées dont les graphiques ont besoin.

    Le jeu complet (1,9 million de lignes, environ 550 Mo en mémoire) n'est
    jamais conservé : seul le résultat agrégé, de quelques centaines de lignes,
    est mis en cache.
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

    # Production par année et par filière (PF1, PF2)
    prod_yearly = _en_twh(
        _aggregate(table, ["Année"], PROD_COLS), PROD_COLS
    ).set_index("Année")

    # Production par région et par filière : verte (PF3, PF4), nucléaire (PF6)
    prod_region = _en_twh(_aggregate(table, ["Région"], PROD_COLS), PROD_COLS)
    green = prod_region[["Région"] + GREEN_NAMES]
    nucleaire = prod_region[["Région", "Nucléaire"]]

    # Solde des échanges physiques par région et par année (DF1), sans 2021 :
    # dans le fichier, la colonne est vide ou décalée pour cette année-là
    distrib = _en_twh(
        _aggregate(table, ["Région", "Année"], ["Ech. physiques (MW)"]),
        ["Ech. physiques (MW)"],
    )
    distrib = distrib[distrib["Année"] != 2021].reset_index(drop=True)

    # Journée type par année (CF4)
    df_daily = _aggregate(table, ["Heure", "Année"], ["Consommation (MW)"], "mean")

    # Consommation par région et par année (CF1)
    cons_yearly = _en_twh(
        _aggregate(table, ["Région", "Année"], ["Consommation (MW)"]),
        ["Consommation (MW)"],
    )

    # Consommation par mois, en moyenne sur les années étudiées (CF2)
    nb_annees = len(pc.unique(table["Année"]))
    cons_monthly = _en_twh(
        _aggregate(table, ["Mois"], ["Consommation (MW)"]), ["Consommation (MW)"]
    )
    cons_monthly["Consommation"] /= nb_annees
    cons_monthly["Mois"] = pd.Categorical(
        cons_monthly["Mois"].map(MOIS_FR), categories=MONTH_ORDER, ordered=True
    )
    cons_monthly = cons_monthly.sort_values("Mois").reset_index(drop=True)

    # Puissance moyenne appelée en France par jour et tranche horaire (CF3).
    # Chaque demi-heure compte une ligne par région : la moyenne d'une ligne
    # multipliée par le nombre de régions donne la consommation nationale.
    weekly = _aggregate(table, ["Jour", "Heure"], ["Consommation (MW)"], "mean")
    weekly["Période"] = weekly["Heure"].map(_periode)
    weekly = (
        weekly.groupby(["Jour", "Période"])["Consommation (MW)"].mean()
        * NB_REGIONS / 1000
    ).rename("Consommation (GW)").reset_index()
    weekly["Jour"] = pd.Categorical(
        weekly["Jour"].map(JOURS_FR), categories=JOUR_ORDER, ordered=True
    )
    weekly["Période"] = pd.Categorical(
        weekly["Période"], categories=[p[0] for p in PERIODES], ordered=True
    )
    weekly = weekly.sort_values(["Période", "Jour"]).reset_index(drop=True)

    # Production et consommation totales par région (PCF1)
    consprod = _en_twh(
        _aggregate(table, ["Région"], ["Consommation (MW)", "Production (MW)"]),
        ["Consommation (MW)", "Production (MW)"],
    )

    del table
    liberer_memoire()

    return {
        "prod_yearly": prod_yearly,
        "green": green,
        "nucleaire": nucleaire,
        "distrib": distrib,
        "df_daily": df_daily,
        "consprod": consprod,
        "cons_yearly": cons_yearly,
        "cons_monthly": cons_monthly,
        "weekly": weekly,
    }


@st.cache_data(show_spinner="Préparation des taux de charge...")
def load_tco_tch_aggregates(filepath="datasets/tco_tch.parquet"):
    """Moyennes mensuelles par région des taux de charge et de couverture."""
    measures = ["TCH Solaire (%)", "TCH Eolien (%)", "TCO Nucléaire (%)"]
    tco_tch = pq.read_table(filepath, columns=["Région", "Mois"] + measures).to_pandas()

    grouped = {}
    for measure in measures:
        table = tco_tch.groupby(["Région", "Mois"])[measure].mean().reset_index()
        table["Mois"] = pd.Categorical(
            table["Mois"].map(MOIS_FR), categories=MONTH_ORDER, ordered=True
        )
        grouped[measure] = table.sort_values(by="Mois")

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


def visualisation():
    "Contenu de la page de la page visualisation"
    aggregates = load_eco2mix_aggregates()
    green = aggregates["green"]
    EUROPE_DATA = load_europe_data()

    st.title("Analyses et visualisations")

    def create_pf1_chart(prod):
        # Notre première Data Viz PF1
        # Production par année de toutes les énergies (déjà agrégée)

        # Calcul de la production totale
        prod_total = prod.sum(axis=1)

        # Calcul du pourcentage de la production totale
        prod_percentage = prod.divide(prod_total, axis=0) * 100

        # Création d'un bar chart avec plotly pour la production secteur/année
        trace_list = []
        for sector in prod_percentage.columns:
            trace = go.Bar(
                x=prod_percentage.index,
                y=prod_percentage[sector],
                name=sector,
                marker=dict(color=colors[sector]),
            )
            trace_list.append(trace)

        # Personnalisation du graphique
        layout = go.Layout(
            barmode="stack",  # Barres empilées
            title="Production par secteur, empilée par année (% du total)",
            xaxis=dict(title="Année"),
            yaxis=dict(title="Pourcentage de la production totale"),
        )

        # Création puis affichage de la figure contenant nos 2 objets
        fig = go.Figure(data=trace_list, layout=layout)

        return fig

    def create_pf2_chart(prod):
        # Production verte par année (déjà agrégée)
        green_yearly = prod[GREEN_NAMES]

        # Reset the index to make 'Année' a regular column
        green_yearly = green_yearly.reset_index()

        fig = px.bar(
            green_yearly,
            x="Année",
            y=green_yearly.columns[1:],  # Exclude 'Année' from the y-values
            title="Évolution de la production d'électricité renouvelable par année",
            labels={"Année": "Année", "value": "Production (TWh)", "variable": "Filière"},
            height=400,
            color_discrete_map=colors,
        )

        fig.update_layout(barmode="stack")

        return fig

    def create_pf3_chart(df):
        # Création d'un DataFrame regroupant la production verte/région

        fig = px.bar(
            green,
            x="Région",
            y=green.columns[1:],
            title="Production d'électricité renouvelable par région, cumulée de 2013 à 2021",
            labels={"Région": "Région", "value": "Production (TWh)", "variable": "Filière"},
            height=400,
            color_discrete_map=colors,
        )

        fig.update_layout(barmode="stack")

        return fig

    def create_pf4_chart(df, type_energie):
        try:
            fig = px.pie(
                df,
                names="Région",
                values=type_energie,
                color_discrete_sequence=px.colors.sequential.Greens_r,
                title=f"Répartition de la production {type_energie.lower()} par région (2013-2021)",
            )
            return fig
        except Exception as e:
            st.error(f"Il y a eu une erreur : {e}")
            return None

    def create_pf6_chart(nucleaire):
        # Production nucléaire cumulée par région, de la plus forte à la plus faible
        nucleaire = nucleaire.sort_values("Nucléaire", ascending=False)
        fig = px.bar(
            nucleaire,
            x="Région",
            y="Nucléaire",
            title="Production d'électricité nucléaire par région, cumulée de 2013 à 2021",
            labels={"Nucléaire": "Production (TWh)"},
            color_discrete_sequence=[colors["Nucléaire"]],
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1)
        return fig

    # Création du DataFrame 'EUROPE_PROD'

    def create_prod_europe(df):
        return df[df["Type"] == "Production"]

    EUROPE_PROD = create_prod_europe(EUROPE_DATA)

    # Création du DatFrame 'EUROPE_CONS'
    def create_cons_europe(df):
        return df[df["Type"] == "Consommation"]

    EUROPE_CONS = create_cons_europe(EUROPE_DATA)

    def create_pe1a_chart(df):
        EUROPE_PROD_TYPE = (
            EUROPE_PROD.groupby(["Pays", "Class"])["Énergie (TWh)"].sum().reset_index()
        )
        fig = px.bar(
            EUROPE_PROD_TYPE,
            x="Pays",
            y="Énergie (TWh)",
            color="Class",
            labels={"Énergie (TWh)": "Production cumulée (TWh)", "Pays": "Pays"},
            title="Production d'énergie renouvelable par pays, cumulée de 2013 à 2021",
        )

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig

    def create_pe2a_chart(df):
        euro_yearly = (
            EUROPE_PROD.groupby(["Class", "Année"])["Énergie (TWh)"]
            .sum()
            .unstack()
            .transpose()
        )
        fig = px.bar(
            euro_yearly,
            x=euro_yearly.index,
            y=euro_yearly.columns,
            title="Production européenne d'énergie renouvelable par type et par année",
        )
        fig.update_layout(
            barmode="stack",
            xaxis_title="Année",
            yaxis_title="Production (TWh)",
            legend_title="Classification",
        )

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig

    # Variables pour df1 & df2 (2021 est déjà exclue)
    distrib = aggregates["distrib"]

    def create_df1_chart(distrib, region):
        try:
            # Solde annuel en TWh : positif = importations nettes,
            # négatif = exportations nettes vers les autres régions et pays
            fig, ax = plt.subplots(figsize=(10, 6))
            region_data = distrib[distrib["Région"] == region]
            ax.plot(region_data["Année"], region_data["Ech. physiques"], marker="o")
            ax.axhline(0, color="gray", linewidth=1)
            ax.set_title(f"Solde annuel des échanges physiques : {region}")
            ax.set_xlabel("Année")
            ax.set_ylabel("Solde des échanges (TWh)\n< 0 : exportatrice   > 0 : importatrice")
            ax.grid(True)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Erreur : {e}")

    # TCO & TCH
    tco_tch = load_tco_tch_aggregates()
    tco_tch_grouped_solaire = tco_tch["TCH Solaire (%)"]
    tco_tch_grouped_eolien = tco_tch["TCH Eolien (%)"]
    tco_nuke = tco_tch["TCO Nucléaire (%)"]

    def create_tcf1_chart(df):
        fig = px.line(
            tco_tch_grouped_solaire,
            x="Mois",
            y="TCH Solaire (%)",
            color="Région",
            title="TCH Solaire (%) par Mois et Région",
        )

        # Titres
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="TCH Solaire (%)",
            legend_title="Région",
        )

        return fig

    def create_tcf2_chart(df):
        fig = px.line(
            tco_tch_grouped_eolien,
            x="Mois",
            y="TCH Eolien (%)",
            color="Région",
            title="TCH Eolien (%) par Mois et Région",
        )

        # Titres
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="TCH Eolien (%)",
            legend_title="Région",
        )

        return fig

    def create_tcf3_chart(df):
        fig = px.line(
            tco_nuke,
            x="Mois",
            y="TCO Nucléaire (%)",
            color="Région",
            title="TCO Nucléaire (%) par Mois et Région",
        )

        # Titres
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="TCO Nucléaire %",
            legend_title="Région",
        )

        return fig

    df_daily = aggregates["df_daily"]

    def create_cf4_chart(df):
        fig = px.line(
            df_daily,
            x="Heure",
            y="Consommation (MW)",
            color="Année",
            hover_data=["Année"],
            labels={"Consommation (MW)": "Consommation moyenne (MW)"},
        )
        fig.update_layout(title="Consommation dans une journée type, par année")
        return fig

    def create_cf1_chart(cons_yearly):
        fig = px.line(
            cons_yearly,
            x="Année",
            y="Consommation",
            color="Région",
            markers=True,
            title="Consommation d'électricité par région et par année",
            labels={"Consommation": "Consommation (TWh)"},
            # 12 régions : la palette par défaut n'a que 10 couleurs
            color_discrete_sequence=px.colors.qualitative.Dark24,
            category_orders={
                "Région": cons_yearly.groupby("Région")["Consommation"]
                .sum()
                .sort_values(ascending=False)
                .index.tolist()
            },
        )
        fig.update_layout(height=500)
        return fig

    def create_cf2_chart(cons_monthly):
        fig = px.bar(
            cons_monthly,
            x="Mois",
            y="Consommation",
            title="Consommation d'électricité en France par mois (moyenne de 2013 à 2021)",
            labels={"Consommation": "Consommation (TWh)"},
            color="Consommation",
            color_continuous_scale="OrRd",
        )
        fig.update_layout(coloraxis_showscale=False)
        return fig

    def create_cf3_chart(weekly):
        fig = px.line(
            weekly,
            x="Jour",
            y="Consommation (GW)",
            color="Période",
            markers=True,
            title="Consommation moyenne en France selon le jour et le moment de la journée",
            labels={
                "Jour": "Jour de la semaine",
                "Consommation (GW)": "Puissance moyenne appelée (GW)",
            },
        )
        return fig

    def create_pcf1_chart(consprod):
        # Production et consommation totales par région (déjà agrégées)

        # Création d'une visualisation Plotly scatter pour comparer les régions entre elles
        fig = px.scatter(
            consprod,
            x="Production",
            y="Consommation",
            color="Région",
            title="Production et consommation par région, cumulées de 2013 à 2021",
            hover_data=["Région"],
            size="Production",
            size_max=30,
        )

        # Personnalisation du graphique
        fig.update_layout(
            xaxis_title="Production (TWh)",
            yaxis_title="Consommation (TWh)",
            legend_title="Régions",
            xaxis=dict(gridcolor="lightgray"),
            yaxis=dict(gridcolor="lightgray"),
        )

        return fig

    def create_ce3_chart(df):
        EUROPE_CONS_TYPE = (
            df.groupby(["Pays", "Class"])["Énergie (TWh)"].sum().reset_index()
        )

        fig = px.bar(
            EUROPE_CONS_TYPE,
            x="Pays",
            y="Énergie (TWh)",
            color="Class",
            labels={
                "Énergie (TWh)": "Consommation cumulée (TWh)",
                "Pays": "Pays",
                "Class": "Classification",
            },
            title="Consommation d'énergies renouvelables par pays, cumulée de 2013 à 2021",
            # Pays du plus gros au plus petit consommateur
            category_orders={
                "Pays": EUROPE_CONS_TYPE.groupby("Pays")["Énergie (TWh)"]
                .sum()
                .sort_values(ascending=False)
                .index.tolist()
            },
        )

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig

    def create_ce4_chart(df):
        # Graphique CE4
        # Total consommation annuelle  d'énergie renouvelable en Europe par type d'énergie

        # Grouper les données par "Classification" et "Année" et calculer la somme de la consommation
        euro_yearly = (
            df.groupby(["Class", "Année"])["Énergie (TWh)"].sum().unstack()
        )

        euro_yearly = euro_yearly.transpose()

        # Création plotly
        fig = px.bar(
            euro_yearly,
            x=euro_yearly.index,
            y=euro_yearly.columns,
            title="Consommation européenne d'énergies renouvelables par type et par année",
        )
        fig.update_layout(
            barmode="stack",
            xaxis_title="Année",
            yaxis_title="Consommation (TWh)",
            legend_title="Classification",
        )

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig

    """ APRES CETTE LIMITE, ON AJOUTE TOUS LES TITRES, BODY ET APPELS DES FONCTIONS."""

    ### PRODUCTION ###
    st.title("Production de l'énergie")

    # PF1
    pf1_chart = create_pf1_chart(aggregates["prod_yearly"])
    st.plotly_chart(pf1_chart)
    st.info(
        "Dépendance au nucléaire : Le graphique révèle que la France dépend largement de l'énergie nucléaire pour sa production d'électricité. Cette source d'énergie représente une part substantielle de la production totale, ce qui indique son importance dans le mix énergétique du pays. La France a historiquement investi massivement dans l'énergie nucléaire, ce qui lui a permis de disposer d'une source d'énergie fiable et à faible émission de carbone. Nous pourrons comparer cette stratégie au reste de l'Europe plus tard dans ce rapport."
    )

    # PF2
    pf2_chart = create_pf2_chart(aggregates["prod_yearly"])
    st.plotly_chart(pf2_chart)
    st.info(
        "La production d'électricité renouvelable progresse, portée par l'éolien et le solaire : la production éolienne passe de 16 TWh en 2013 à 40 TWh en 2020 (36 TWh en 2021), et la production solaire de 4,5 à 14 TWh. À elles deux, ces filières passent de moins de 4 % à près de 10 % de la production d'électricité du pays. L'hydraulique reste la première source renouvelable, avec 53 à 75 TWh par an selon la pluviométrie : c'est elle qui fait varier le total d'une année sur l'autre. Cette croissance montre que la France diversifie son mix électrique, dans une logique de réduction des émissions de gaz à effet de serre."
    )

    # PF3
    pf3_chart = create_pf3_chart(green)
    st.plotly_chart(pf3_chart)
    st.info(
        "Ce graphique illustre les disparités de production d'électricité renouvelable entre les régions, en cumul de 2013 à 2021. Auvergne-Rhône-Alpes se distingue nettement (environ 280 TWh), grâce à une production hydraulique bien supérieure à celle des autres régions. Elle est suivie, loin derrière, par l'Occitanie (environ 155 TWh) et le Grand Est (environ 140 TWh), puis par Provence-Alpes-Côte d'Azur (environ 110 TWh) : dans ces trois régions aussi, l'hydraulique domine, grâce aux Pyrénées, au Rhin et aux Alpes. Le Grand Est et les Hauts-de-France se démarquent pour l'éolien, dont ils assurent à eux deux près de la moitié de la production. Sans surprise, le solaire est surtout exploité dans le sud : la Nouvelle-Aquitaine, l'Occitanie et Provence-Alpes-Côte d'Azur en produisent près des deux tiers. Enfin, la bioénergie est présente dans toutes les régions."
    )

    # PF4

    st.warning(
        "Sélectionnez un type d'énergie verte pour voir son split de production par région",
        icon="🤖",
    )
    type_energies = green.columns[1:]
    selected_energy = st.selectbox("Type d'énergie:", type_energies)

    pf4_chart = create_pf4_chart(green, selected_energy)
    st.plotly_chart(pf4_chart)

    # PF5
    st.subheader("Éolien en mer et éolien terrestre")
    st.info(
        "Sur la période étudiée (2013-2021), toute la production éolienne française est terrestre : le premier parc éolien en mer, au large de Saint-Nazaire, n'a été mis en service qu'en 2022. Les colonnes « Eolien terrestre » et « Eolien offshore » du jeu Eco2Mix ne sont remplies qu'en 2021, et leurs valeurs ne correspondent pas à de l'éolien : la colonne « offshore » n'est non nulle que dans les sept régions qui ont des centrales nucléaires, y compris Auvergne-Rhône-Alpes, qui n'a pas de façade maritime. Ces colonnes sont décalées par rapport à leur intitulé, et nous ne les utilisons donc pas."
    )

    # PF6
    st.subheader("Production nucléaire par région")
    pf6_chart = create_pf6_chart(aggregates["nucleaire"])
    st.plotly_chart(pf6_chart)

    st.info(
        "Sur ce graphique, nous observons les régions qui produisent de l'électricité dans des centrales nucléaires. Seules sept régions sont concernées, et Auvergne-Rhône-Alpes, le Grand Est et le Centre-Val de Loire en sont les principales productrices, avec 650 à 750 TWh chacune sur la période. Comme le nucléaire représente entre 67 % et 77 % de la production d'électricité française selon les années, toutes les régions en dépendent, y compris celles qui n'en produisent pas et qui l'importent. La partie « Distribution » montre que cinq de ces sept régions (Auvergne-Rhône-Alpes, Centre-Val de Loire, Grand Est, Normandie et Nouvelle-Aquitaine) sont exportatrices nettes chaque année de 2013 à 2020. L'Occitanie reste importatrice, et les Hauts-de-France ne deviennent exportateurs qu'à partir de 2018."
    )

    st.title("Focus sur TCO & TCH")
    st.info(
        "Le taux de charge d'une filière se réfère à la quantité de production par rapport à la capacité de production totale en service de cette filière.",
        icon="ℹ️",
    )

    tcf1_chart = create_tcf1_chart(tco_tch)
    st.plotly_chart(tcf1_chart)
    st.write(
        "Le graphique présent affiche les moyennes des taux de charge pour l'énergie solaire, mettant en évidence des pics naturels pendant les mois estivaux, lorsque l'ensoleillement est plus intense. La moyenne maximale se situe aux alentours de 50%. Ce qui ressort de cette analyse, c'est que les régions générant la plus grande quantité d'énergie solaire ont généralement des taux de charge moyens plus bas. Ceci s'explique par la plus grande taille de leurs installations par rapport à d'autres régions. Par exemple, la région Centre-Val de Loire ne contribue qu'à 3 % de la production solaire totale, mais elle détient le record du taux de charge moyen, près de 50 % en juillet."
    )

    tcf2_chart = create_tcf2_chart(tco_tch)
    st.plotly_chart(tcf2_chart)
    st.write(
        "Le graphique ci-dessous illustre le taux de charge éolien, mettant en évidence des pics pendant la saison hivernale. On observe un taux de charge moyen record pour les régions Grand Est et Centre, dépassant les 50% en février. Ces deux régions contribuent respectivement à 22% et 8% de la production éolienne en France. En revanche, la région Hauts-de-France, qui représente près de 26 % de la production éolienne totale, affiche un taux de charge moyen maximal un peu plus bas, autour de 49 %, ce qui s'explique également par la taille de ses installations."
    )

    st.info(
        "Le taux de couverture d’une filière de production au sein d’une région représente la part de cette filière dans la consommation de cette région.",
        icon="ℹ️",
    )
    tcf3_chart = create_tcf3_chart(tco_tch)
    st.plotly_chart(tcf3_chart)
    st.write(
        "Nous choisissons ici d'observer les variations du taux de couverture du nucléaire, pour observer les différences des tendances entre les régions au cours de l'année.​ Ce que nous pouvons voir très clairement, c'est que la région Centre Val de Loire se démarque tout particulièrement, car c'est une région fortement productrice, mais peu consommatrice, et son taux de couverture est largement au-dessus de 100% lorsque la consommation est moins forte dans cette région.​"
    )

    st.header("Donnée de la production des Pays Européens")

    pe1a_chart = create_pe1a_chart(EUROPE_PROD)
    st.plotly_chart(pe1a_chart)
    st.info(
        "Le graphique montre la production d'énergies renouvelables cumulée de 2013 à 2021, toutes formes d'énergie confondues (pas seulement l'électricité). L'Allemagne est en tête (environ 9 900 TWh), suivie de la France et de l'Italie presque à égalité (environ 5 700 et 5 600 TWh), puis de la Suède (environ 4 200 TWh). Les facteurs influençant ces résultats incluent les ressources naturelles, les politiques gouvernementales, les investissements dans les technologies écologiques, ainsi que la taille et la consommation énergétique des pays. En Allemagne, l'accent est mis sur l'éolien, le solaire photovoltaïque et la biomasse grâce à l'initiative Energiewende. La France, bien que dépendante du nucléaire, cherche à diversifier son mix énergétique en favorisant les énergies renouvelables, en particulier l'hydroélectricité. L'Italie se distingue par son potentiel en énergie solaire photovoltaïque, tandis que la Suède mise sur l'hydroélectricité et la bioénergie pour atteindre une production énergétique 100% renouvelable d'ici 2040. L'Allemagne et la France se démarquent également dans les biocarburants et la bioénergie, grâce à des politiques favorables, des ressources agricoles abondantes et des incitations financières pour la production d'énergie à partir de résidus organiques."
    )

    pe2a_chart = create_pe2a_chart(EUROPE_PROD)
    st.plotly_chart(pe2a_chart)
    st.info(
        "De 2013 à 2021, la production européenne d'énergie renouvelable progresse surtout, en volume, grâce aux biocarburants (+585 TWh), à la bioénergie (+208 TWh) et à l'éolien (+177 TWh). En proportion, les plus fortes hausses sont celles des pompes à chaleur (production multipliée par 3,2), du solaire photovoltaïque (multipliée par 2) et de l'éolien (multipliée par 1,85). L'hydraulique, elle, recule légèrement."
    )

    st.title("Distribution de l'énergie")

    st.warning("Sélectionnez une région pour afficher le graphique", icon="🤖")
    regions = distrib["Région"].unique()
    selected_region = st.selectbox("Région", regions)
    create_df1_chart(distrib, selected_region)

    st.image("images/distrib_map.png")
    st.info(
        "La carte montre, pour l'année 2013, en rouge les régions importatrices et en bleu les exportatrices. Ces tendances restent stables jusqu'en 2020, à deux nuances près : les exportations nettes de la Normandie diminuent de plus de moitié (49 TWh en 2013, 21 TWh en 2020), et les Hauts-de-France passent d'importateurs à exportateurs nets à partir de 2018. Les échanges de 2021 ne sont pas exploitables dans notre jeu de données."
    )

    ### CONSOMMATION ###

    st.title("Consommation de l'énergie")
    # CF1
    st.plotly_chart(create_cf1_chart(aggregates["cons_yearly"]))

    # CF2
    st.plotly_chart(create_cf2_chart(aggregates["cons_monthly"]))

    # CF3
    st.plotly_chart(create_cf3_chart(aggregates["weekly"]))

    # CF4

    cf4_chart = create_cf4_chart(df_daily)
    st.plotly_chart(cf4_chart)

    # CF5 &/ou 6

    # CF7

    st.header("Focus sur la population, ajout des données de l'INSEE.")
    st.info(
        'Nous avons créé un ratio "Consommation Per Capita" pour comparer les régions entre elles. Consommation Totale / Nombre d\'habitants',
        icon="🏘️",
    )
    st.image("images/CF7.png")
    st.write(
        "La consommation par habitant médiane des régions du sud est un peu plus élevée que celle des régions du nord, surtout en 2013 et 2014. L'écart se réduit ensuite, et s'inverse légèrement en 2021. Les boîtes se recouvrent largement chaque année : la différence entre nord et sud reste faible."
    )

    # CF8 / 9 / 11

    st.title("Comparaison de la production et de la consommation de l'énergie")

    pcf1_chart = create_pcf1_chart(aggregates["consprod"])
    st.plotly_chart(pcf1_chart)
    st.write(
        "Ce nuage de points compare la production et la consommation d'électricité de chaque région, cumulées de 2013 à 2021. Auvergne-Rhône-Alpes est la première productrice (environ 1 050 TWh) et l'une des deux plus grosses consommatrices (environ 590 TWh). Le Grand Est, le Centre-Val de Loire et la Normandie produisent bien plus qu'ils ne consomment : le Centre-Val de Loire produit environ quatre fois sa consommation. À l'inverse, la Bourgogne-Franche-Comté, la Bretagne et les Pays de la Loire ne produisent que 15 à 25 % environ de ce qu'ils consomment, et l'Île-de-France, première consommatrice (environ 635 TWh), à peine 5 %. Ces régions dépendent des échanges avec les régions productrices."
    )

    st.header("La sobriété énergétique")
    st.info(
        "Le secteur de l'électricité en France implique plusieurs acteurs clés, notamment RTE pour le transport, Enedis pour la distribution, et EDF pour la production. Dans les données d'Enedis Open Data pour 2022 et 2023, trois catégories de consommateurs sont distinguées : résidentiels, professionnels, et entreprises, avec des économies d'énergie lors de températures plus élevées l'hiver."
    )
    st.image("images/PCF2.png")
    st.info(
        "La différence entre les résidentiels et les entreprises/professionnels, peut s'expliquer par la nature de leur comportement en terme de dépenses énergétiques: En effet, les résidentiels ont des habitudes plus réactive (Je baisse, j'augmente) alors que les entreprises et les professionnels sont plutôt proactifs, et ne touchent bien souvent pas au thermostat pour rester stable.​"
    )

    st.title("Consommation des énergies renouvelables en Europe")

    st.plotly_chart(create_ce4_chart(EUROPE_CONS))

    st.plotly_chart(create_ce3_chart(EUROPE_CONS))
    st.write(
        "La consommation d'énergies renouvelables en Europe connaît une croissance significative, stimulée par des politiques environnementales strictes, des objectifs de réduction des émissions et des incitations financières. Les biocarburants gagnent en popularité pour diversifier les transports, tandis que la bioénergie prospère grâce aux ressources forestières et agricoles abondantes. L'énergie hydraulique et éolienne est privilégiée dans des régions adaptées, tandis que le biogaz et les déchets municipaux renouvelables sont encouragés pour une gestion durable des déchets. Les pompes à chaleur, le solaire, et la géothermie sont préférés en fonction des ressources locales, tandis que l'énergie océanique est encore en développement."
    )
