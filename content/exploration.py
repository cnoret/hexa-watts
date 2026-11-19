"""
Creation of the "Exploration des données" page for the Hexa Watts application
"""

import streamlit as st
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pandas as pd

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
    nan_info = pd.concat(
        [nan_count, (nan_count / n_rows * 100).round(2)],
        axis=1,
        keys=["NaN Count", "% of NaN"],
    )
    return {"n_rows": n_rows, "n_cols": len(columns), "head": head, "nan_info": nan_info}


# Cache for loading the temperature dataset
@st.cache_data
def load_temperature_dataset(filepath, separator=";"):
    """Load the temperature dataset from a CSV file"""
    return pd.read_csv(filepath, sep=separator)


def exploration():
    """Page for data exploration"""
    st.title("Exploration des données")

    # Display image
    image_url = "images/diggy.png"
    st.image(image_url, width=200)

    # Load datasets with caching
    with st.spinner("Chargement des données...⏳"):
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

    # Display information about the main dataset
    st.subheader("Aperçu du jeu de données principal : Eco2Mix (RTE)")
    st.write("Nombre de lignes :", summary["n_rows"])
    st.write("Nombre de colonnes :", summary["n_cols"])
    st.write("Échantillon de données :")
    st.dataframe(summary["head"])

    # Display missing value information
    st.subheader("Aperçu des valeurs manquantes")
    st.write(summary["nan_info"])

    # Display information about the temperature dataset
    st.subheader("Aperçu du jeu de données des températures")
    st.write("Nombre de lignes :", temp.shape[0])
    st.write("Nombre de colonnes :", temp.shape[1])
    st.write("Échantillon de données :")
    st.dataframe(temp.head())
    st.write("Nombre de valeurs manquantes :", temp.isna().sum().sum())
