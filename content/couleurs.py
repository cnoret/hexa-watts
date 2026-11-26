"""
Couleurs des filières, partagées par la page Analyses et la page Préparation
pour que les graphiques et leur documentation restent identiques.
Les teintes sont choisies pour rester lisibles sur fond clair comme sur fond sombre.
"""

# Filières de production d'électricité (Eco2Mix)
COULEURS_FILIERES = {
    "Thermique": "#E5484D",  # Rouge
    "Nucléaire": "#F5C542",  # Ambre
    "Eolien": "#5EC8E5",  # Bleu ciel
    "Solaire": "#F0913A",  # Orange
    "Hydraulique": "#3E63DD",  # Bleu
    "Bioénergies": "#46A758",  # Vert
}

# Types d'énergie renouvelable (Eurostat)
COULEURS_EUROPE = {
    "Bioénergie": "#E5484D",  # Rouge
    "Déchets municipaux renouvelables": "#46A758",  # Vert
    "Éolien": "#5EC8E5",  # Bleu ciel
    "Solaire Photovoltaique": "#F0913A",  # Orange
    "Solaire Thermique": "#F5C542",  # Ambre
    "Hydraulique": "#3E63DD",  # Bleu
    "Biogaz": "#A0A8B8",  # Gris clair
    "Biocarburants": "#8E7CF0",  # Violet
    "Pompe à chaleur": "#E377C2",  # Rose (le rouge est déjà pris par la bioénergie)
    "Océan": "#12A594",  # Turquoise
    "Geothermique": "#C9A0FF",  # Lavande
}
