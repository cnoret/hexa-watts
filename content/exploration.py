"""
Création de la page "Exploration des données" de l'application Énergie_France
"""

import streamlit as st
import pyarrow.parquet as pq
import pandas as pd

def exploration():
    "Page d'exploration"
    st.title("Exploration des données")

    # Image
    image_url = "images/diggy.png"
    st.image(image_url, width=200)

    with st.spinner('Chargement des données...⏳'):
        try:
            table = pq.read_table('datasets/df.parquet')
            df = table.to_pandas()

            # Création de notre DataFrame "temp" contenant les températures
            temp = pd.read_csv('datasets/temp.csv', sep = ';')

            # Suppression de la colonne vide
            df = df.drop(["Column 30"], axis = 1)

            # Calcul du pourcentage de valeur manquantes du dataframe
            nan_count = df.isna().sum()
            nan_percentage = (df.isna().mean() * 100).round(2)
            nan_info = pd.concat([nan_count, nan_percentage],
                                 axis = 1, keys = ['NaN Count', '% of NaN'])

        except pd.errors.EmptyDataError as e:
            st.error(f"Une erreur s'est produite lors de la lecture du fichier CSV : {str(e)}")
            return

        except FileNotFoundError as e:
            st.error(f"Le fichier spécifié est introuvable : {str(e)}")
            return

        except KeyError as e:
            st.error(f"La colonne spécifiée est introuvable dans le DataFrame : {str(e)}")
            return

        except Exception as e:
            st.error(f"Une erreur inattendue s'est produite : {str(e)}")
            return

    # Display
    st.subheader("Aperçu du jeu de données principal : Eco2Mix (RTE)")
    st.write("Nombre de lignes :", df.shape[0])
    st.write("Nombre de colonnes :", df.shape[1])
    st.write("Échantillon de données :")
    st.dataframe(df.head())

    st.subheader("Aperçu des valeurs manquantes")
    st.write(nan_info)

    st.subheader("Aperçu du jeu de données des températures")
    st.write("Nombre de lignes :", temp.shape[0])
    st.write("Nombre de colonnes :", temp.shape[1])
    st.write("Échantillon de données :")
    st.dataframe(temp.head())
    st.write("Nombre de valeurs manquantes :", temp.isna().sum().sum())
