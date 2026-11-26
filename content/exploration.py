"""
Creation of the "Exploration des données" page for the Hexa Watts application
"""

import pandas as pd
import plotly.express as px
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import streamlit as st

from content.interface import en_tete, graphique, indicateurs, nombre_fr
from content.memoire import liberer_memoire


DROPPED_COLUMNS = ["Column 30"]


# Cache for the main dataset summary
@st.cache_data(show_spinner=False)
def load_main_dataset_summary(filepath, n_head=5):
    """
    Résumé du jeu Eco2Mix sans le charger entièrement en mémoire.

    Le fichier complet occupe environ 2 Go une fois converti en DataFrame,
    ce qui dépasse la mémoire disponible sur Streamlit Community Cloud.
    On lit donc une colonne à la fois : on en garde les premières lignes pour
    l'aperçu et on compte ses valeurs manquantes, puis on la libère.
    """
    parquet_file = pq.ParquetFile(filepath)
    schema = parquet_file.schema_arrow
    columns = [name for name in schema.names if name not in DROPPED_COLUMNS]
    n_rows = parquet_file.metadata.num_rows

    head_columns = {}
    nan_count = {}
    for name in columns:
        column = parquet_file.read(columns=[name]).column(0)
        # take() copie les lignes : le reste de la colonne peut être libéré
        head_columns[name] = column.take(list(range(min(n_head, n_rows))))
        count = column.null_count
        if pa.types.is_floating(column.type):
            # Les NaN ne sont pas toujours stockés comme valeurs nulles
            count += pc.sum(pc.is_nan(column.drop_null())).as_py() or 0
        nan_count[name] = count
        del column

    head_schema = pa.schema(
        [schema.field(name) for name in columns], metadata=schema.metadata
    )
    head = pa.table(head_columns, schema=head_schema).to_pandas()
    liberer_memoire()

    nan_count = pd.Series(nan_count)
    nan_info = pd.DataFrame(
        {
            "Valeurs manquantes": nan_count,
            "Remplissage (%)": (100 - nan_count / n_rows * 100).round(2),
        }
    )
    return {"n_rows": n_rows, "n_cols": len(columns), "head": head, "nan_info": nan_info}


# Cache for loading the temperature dataset
@st.cache_data
def load_temperature_dataset(filepath, separator=";"):
    """Load the temperature dataset from a CSV file"""
    return pd.read_csv(filepath, sep=separator)


def exploration():
    """Page for data exploration"""
    en_tete(
        "Exploration des données",
        surtitre="Étape 1 · Les données brutes",
        sous_titre="Ce que contiennent les jeux Eco2Mix et Météo France avant tout traitement.",
    )

    # Load datasets with caching
    with st.spinner("Chargement des données..."):
        try:
            # Load main dataset summary
            summary = load_main_dataset_summary("datasets/df.parquet")

            # Load temperature dataset
            temp = load_temperature_dataset("datasets/temp.csv")

        except pd.errors.EmptyDataError as e:
            st.error(
                f"Une erreur s'est produite lors de la lecture du fichier CSV : {str(e)}"
            )
            return

        except FileNotFoundError as e:
            st.error(f"Le fichier spécifié est introuvable : {str(e)}")
            return

        except KeyError as e:
            st.error(
                f"La colonne spécifiée est introuvable dans le DataFrame : {str(e)}"
            )
            return

        except Exception as e:
            st.error(f"Une erreur inattendue s'est produite : {str(e)}")
            return

    # Jeu principal
    st.subheader("Jeu de données principal : Eco2Mix (RTE)")
    indicateurs(
        [
            ("Lignes", nombre_fr(summary["n_rows"]), "une par région et par demi-heure"),
            ("Colonnes", str(summary["n_cols"]), None),
            ("Températures", nombre_fr(temp.shape[0]), "relevés journaliers par région"),
        ]
    )
    st.dataframe(summary["head"], hide_index=True)

    # Valeurs manquantes
    graphique(graphique_remplissage(summary["nan_info"]))
    with st.expander("Nombre de valeurs manquantes par colonne"):
        st.dataframe(summary["nan_info"])

    # Températures
    st.subheader("Jeu de données des températures")
    manquantes = int(temp.isna().sum().sum())
    st.caption(
        f"{temp.shape[0]} lignes, {temp.shape[1]} colonnes, "
        + ("aucune valeur manquante." if manquantes == 0 else f"{manquantes} valeurs manquantes.")
    )
    st.dataframe(temp.head(), hide_index=True)


def graphique_remplissage(nan_info):
    """Taux de remplissage de chaque colonne, les moins remplies en haut."""
    remplissage = nan_info["Remplissage (%)"].sort_values(ascending=False)
    incompletes = int((remplissage < 100).sum())
    fig = px.bar(
        x=remplissage.to_numpy(),
        y=remplissage.index,
        orientation="h",
        title=f"{incompletes} colonnes sur {len(remplissage)} ont des valeurs manquantes",
        labels={"x": "Taux de remplissage (%)", "y": ""},
        height=max(360, 140 + 22 * len(remplissage)),
    )
    fig.update_traces(
        marker_color=["#2E5EAA" if v == 100 else "#F39237" for v in remplissage],
        hovertemplate="%{y} : %{x:.2f} %<extra></extra>",
    )
    fig.update_xaxes(range=[0, 100])
    return fig
