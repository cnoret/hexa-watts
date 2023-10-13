import pandas as pd
import pyarrow.parquet as pq
import numpy as np

table = pq.read_table('datasets/df.parquet')
df = table.to_pandas()

# Suppression de la colonne vide
df = df.drop(["Column 30"], axis = 1)

## Notre dataset est très propre d'origine, les NaN correspondent uniquement
## à une production/consommation nulle. Nous pourrions simplement boucler sur
## l'intégralité du dataset mais allons procéder en découpage par étapes.
## Les valeurs manquantes des TCO/TCH seront traités dans un focus dédié.

# Traitement des NaN : Nucléaire
df['Nucléaire (MW)'] = df['Nucléaire (MW)'].fillna(0)

# Traitement des NaN : Pompage
regions_sans_pompage = ['Centre-Val de Loire', 'Normandie', 'Nouvelle-Aquitaine',
                      'Pays de la Loire', 'Île-de-France']

# Remplacement des NaN des régions sans stations par une valeur nulle
df.loc[df['Région'].isin(regions_sans_pompage), 'Pompage (MW)'] = \
df.loc[df['Région'].isin(regions_sans_pompage), 'Pompage (MW)'].fillna(0)

# Remplacement des NaN des HDF par une valeur nulle
df.loc[df['Région'].isin(['Hauts-de-France']), 'Pompage (MW)'] = \
df.loc[df['Région'].isin(['Hauts-de-France']), 'Pompage (MW)'].fillna(0)

# Traitement des NaN : Distribution Nationale et Batteries
df['Ech. physiques (MW)'] = df['Ech. physiques (MW)'].fillna(0)
df['Stockage batterie'] = df['Stockage batterie'].fillna(0)
df['Déstockage batterie'] = df['Déstockage batterie'].fillna(0)

# Traitement des NaN : Éolien
df['Eolien terrestre'] = df['Eolien terrestre'].fillna(0)
df['Eolien offshore'] = df['Eolien offshore'].fillna(0)
df['Eolien (MW)'] = df['Eolien (MW)'].fillna(0)

# Ajout de colonnes temporelles
df['Date - Heure'] = pd.to_datetime(df['Date - Heure'],
                                    format = '%Y-%m-%d %H:%M:%S%z',
                                    errors = 'coerce', utc = True)
df['Jour'] = df['Date - Heure'].dt.day_name() # Ajout du jour de la semaine
df['Jour_mois'] = df['Date - Heure'].dt.day # Jour du mois
df['Mois'] = df['Date - Heure'].dt.month_name() # Mois de l'année
df['Année'] = df['Date - Heure'].dt.year # Année

# Création d'une colonne Week-end pour indiquer s'il s'agit d'un
# jour de la semaine ou d'un week-end.
week_end = ['Saturday', 'Sunday']
df['Week-End'] = df['Jour'].apply(lambda day: 1 if day in week_end else 0)

## Dans notre étude, nous souhaitons conserver que les années complètes,
## nous supprimons donc 2022 du scope.
df = df[(df['Année'] != 2022) & (df['Année'] > 2012)].copy()

# Ajout d'une colonne qui indique la somme de production totale confondue
df.loc[:, 'Production (MW)'] = df['Bioénergies (MW)'] + df['Eolien (MW)']  \
                        + df['Hydraulique (MW)'] + df['Nucléaire (MW)'] \
                        + df['Solaire (MW)'] + df['Thermique (MW)']

## Pendant certaines périodes de trente minutes, certaines régions ne produisent
## pas d'énergie, ce qui conduit à des valeurs manquantes dans les données.
## Ces valeurs NaN sont donc remplacées par des zéros.
df.loc[:, 'Production (MW)'] = df['Production (MW)'].fillna(0)

# Ajout d'une colonne 'Cotier' pour déterminer si la région est côtière ou non
cotes = ['Bretagne', 'Normandie','Hauts-de-France',
       'Pays de la Loire','Nouvelle-Aquitaine','Occitanie',
       "Provence-Alpes-Côte d'Azur"]

df['Cotier'] = df['Région'].apply(lambda region: 1 if region in cotes else 0)

# Ajout d'une colonne "Nordsud" pour déterminer la position d'une région
def nordsud(reg):
  "Fonction retournant une chaîne 'Nord' / 'Sud' suivant la région passée en argument"
  nord = ['Bretagne', 'Normandie', 'Pays de la Loire', 'Centre-Val de Loire',
          'Île-de-France', 'Hauts-de-France', 'Grand Est', 'Bourgogne-Franche-Comté']
  sud = ['Nouvelle-Aquitaine', 'Occitanie', 'Auvergne-Rhône-Alpes',
         "Provence-Alpes-Côte d'Azur"]
  if reg in nord:
    return 'Nord'
  elif reg in sud:
    return 'Sud'
  else:
    return np.nan

# Utilisation de notre fonction nordsud sur la colonne Région
df['Nordsud'] = df['Région'].apply(nordsud)

print("NaN de la colonne NordSud :", df['Nordsud'].isna().sum())
print("NaN de la colonne Cotier :", df['Cotier'].isna().sum())
print("NaN de la colonne Week-End :", df['Week-End'].isna().sum())

# Création d'un DataFrame pour l'analyse de la consommation.
to_keep = ['Région', 'Nature', 'Date', 'Heure', 'Date - Heure',
           'Jour','Mois', 'Jour_mois', 'Année', 'Consommation (MW)']
consommation = df[to_keep]

# Création d'un DataFrame pour la consommation par années
yearly = consommation.groupby(['Année', 'Région'])['Consommation (MW)'].sum().reset_index()

# Création d'un DataFrame pour l'analyse de la production
to_loose = ['Consommation (MW)']
production = df.drop(to_loose, axis = 1)

## Création d'un DataFrame pour l'analyse des TCO/TCH
# Sauvegarde de chaque colonnes contenant TCO ou TCH dans son nom
tco_columns = [col for col in df.columns if 'TCO' in col]
tch_columns = [col for col in df.columns if 'TCH' in col]
base_columns = ['Date', 'Région']

# On réassemble les colonnes et on construit un nouveau DataFrame TCO/TCH
selected_columns = base_columns + tco_columns + tch_columns
tco_tch = df[selected_columns]
df = df.drop(columns = tco_columns + tch_columns)
