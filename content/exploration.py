"""
Creation of the "Exploration des données" page for the Hexa Watts application
"""

import streamlit as st
import pyarrow.parquet as pq
import pandas as pd


# Cache for loading the main dataset
@st.cache_data
def load_main_dataset(filepath):
    """Load the main dataset from a Parquet file"""
    table = pq.read_table(filepath)
    return table.to_pandas()


# Cache for loading the temperature dataset
@st.cache_data
def load_temperature_dataset(filepath, separator=";"):
    """Load the temperature dataset from a CSV file"""
    return pd.read_csv(filepath, sep=separator)


def calculate_missing_values(df):
    """Calculate missing value statistics for a DataFrame"""
    nan_count = df.isna().sum()
    nan_percentage = (df.isna().mean() * 100).round(2)
    return pd.concat(
        [nan_count, nan_percentage], axis=1, keys=["NaN Count", "% of NaN"]
    )


def exploration():
    """Page for data exploration"""
    st.title("Exploration des données")

    # Display image
    image_url = "images/diggy.png"
    st.image(image_url, width=200)

    # Load datasets with caching
    with st.spinner("Chargement des données...⏳"):
        try:
            # Load main dataset
            df = load_main_dataset("datasets/df.parquet")

            # Load temperature dataset
            temp = load_temperature_dataset("datasets/temp.csv")

            # Remove unnecessary column
            if "Column 30" in df.columns:
                df = df.drop(["Column 30"], axis=1)

            # Calculate missing value statistics
            nan_info = calculate_missing_values(df)

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
    st.write("Nombre de lignes :", df.shape[0])
    st.write("Nombre de colonnes :", df.shape[1])
    st.write("Échantillon de données :")
    st.dataframe(df.head())

    # Display missing value information
    st.subheader("Aperçu des valeurs manquantes")
    st.write(nan_info)

    # Display information about the temperature dataset
    st.subheader("Aperçu du jeu de données des températures")
    st.write("Nombre de lignes :", temp.shape[0])
    st.write("Nombre de colonnes :", temp.shape[1])
    st.write("Échantillon de données :")
    st.dataframe(temp.head())
    st.write("Nombre de valeurs manquantes :", temp.isna().sum().sum())
