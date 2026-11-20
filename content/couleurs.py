"""
Couleurs des filières, partagées par la page Analyses et la page Préparation
pour que les graphiques et leur documentation restent identiques.
"""

# Filières de production d'électricité (Eco2Mix)
COULEURS_FILIERES = {
    "Thermique": "red",
    "Nucléaire": "#F7E237",
    "Eolien": "lightblue",
    "Solaire": "orange",
    "Hydraulique": "darkblue",
    "Bioénergies": "green",
}

# Types d'énergie renouvelable (Eurostat)
COULEURS_EUROPE = {
    "Bioénergie": "#FF0000",  # Rouge
    "Déchets municipaux renouvelables": "#00FF00",  # Vert
    "Éolien": "#ADD8E6",  # Bleu clair
    "Solaire Photovoltaique": "#FFA500",  # Orange
    "Solaire Thermique": "#FFFF00",  # Jaune
    "Hydraulique": "#00008B",  # Bleu foncé
    "Biogaz": "#808080",  # Gris
    "Biocarburants": "#800080",  # Violet
    "Pompe à chaleur": "#E377C2",  # Rose (le rouge est déjà pris par la bioénergie)
    "Océan": "#0000FF",  # Bleu
    "Geothermique": "#D076FF",  # Violet clair
}
