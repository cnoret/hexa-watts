"""
Éléments d'interface communs à toutes les pages : style, en-tête de page,
indicateurs clés et pied de page.

Le thème lui-même (couleurs, polices, arrondis) est défini dans
.streamlit/config.toml. Ce module n'ajoute que ce que le thème ne couvre pas.
"""

from html import escape

import streamlit as st


def _option(nom, defaut):
    """Valeur d'une option du thème (.streamlit/config.toml), ou sa valeur par défaut."""
    return st.get_option(f"theme.{nom}") or defaut


def _style():
    """Règles CSS, aux couleurs du thème courant."""
    accent = _option("primaryColor", "#2E5EAA")
    fond_carte = _option("secondaryBackgroundColor", "#FFFFFF")
    bordure = _option("borderColor", "#E3E8F0")
    sombre = _option("base", "light") == "dark"
    gris = "#8A93A6" if sombre else "#6B778C"
    texte_pied = "#C2C7D3" if sombre else "#3B4559"
    return f"""
<style>
/* Surtitre au-dessus du titre de page, comme un fil d'Ariane */
.hw-surtitre {{
    color: {accent};
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: -0.6rem;
}}
.hw-sous-titre {{
    color: {gris};
    font-size: 1.05rem;
    margin-top: -0.8rem;
    margin-bottom: 1.2rem;
}}
/* Cartes d'indicateurs */
[data-testid="stMetric"] {{
    background: {fond_carte};
}}
/* Chaque graphique dans une carte */
[data-testid="stPlotlyChart"] {{
    background: {fond_carte};
    border: 1px solid {bordure};
    border-radius: 12px;
    overflow: hidden;
}}
[data-testid="stMetricValue"] {{
    font-weight: 700;
}}
/* Pied de page */
.hw-pied {{
    border-top: 1px solid {bordure};
    margin-top: 3rem;
    padding-top: 1.2rem;
    color: {gris};
    font-size: 0.85rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 1.6rem;
    justify-content: space-between;
}}
.hw-pied a {{ color: {gris}; text-decoration: none; }}
.hw-pied a:hover {{ color: {accent}; }}
.hw-pied strong {{ color: {texte_pied}; font-weight: 600; }}
</style>
"""

EQUIPE = [
    {
        "nom": "Simon Berry",
        "liens": {
            "LinkedIn": "https://www.linkedin.com/in/simon-berry56/",
            "GitHub": "https://github.com/sibmel29",
        },
    },
    {
        "nom": "Siham Houchi",
        "liens": {"LinkedIn": "https://www.linkedin.com/in/siham-houchi-19622a15a/"},
    },
    {
        "nom": "Christophe Noret",
        "liens": {
            "LinkedIn": "https://www.linkedin.com/in/cnoret",
            "GitHub": "https://github.com/cnoret",
        },
    },
]


def appliquer_style():
    """Ajoute à la page les quelques règles CSS propres à l'application."""
    st.html(_style())


def en_tete(titre, surtitre=None, sous_titre=None):
    """Titre de page, précédé d'un surtitre et suivi d'une phrase d'accroche."""
    if surtitre:
        st.markdown(
            f"<div class='hw-surtitre'>{escape(surtitre)}</div>",
            unsafe_allow_html=True,
        )
    st.title(titre, anchor=False)
    if sous_titre:
        st.markdown(
            f"<p class='hw-sous-titre'>{escape(sous_titre)}</p>",
            unsafe_allow_html=True,
        )


def indicateurs(valeurs):
    """
    Rangée de cartes d'indicateurs clés.

    `valeurs` est une liste de tuples (libellé, valeur, commentaire) ; le
    commentaire, facultatif, s'affiche sous la valeur sans flèche ni couleur
    pour ne pas laisser croire qu'une hausse est forcément une bonne nouvelle.
    """
    for colonne, (libelle, valeur, commentaire) in zip(
        st.columns(len(valeurs)), valeurs, strict=True
    ):
        colonne.metric(
            libelle,
            valeur,
            commentaire,
            delta_color="off",
            delta_arrow="off",
            border=True,
        )


def pied_de_page():
    """Équipe du projet et liens, en bas de chaque page."""
    membres = " · ".join(
        f"<strong>{escape(m['nom'])}</strong> "
        + " ".join(
            f"<a href='{url}' target='_blank' rel='noopener noreferrer'>{reseau}</a>"
            for reseau, url in m["liens"].items()
        )
        for m in EQUIPE
    )
    st.markdown(
        f"""
        <div class='hw-pied'>
            <span>Projet Énergie France : {membres}</span>
            <span>Refonte Hexa Watts : <strong>Christophe Noret</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nombre_fr(valeur, decimales=0, signe=False):
    """
    Nombre au format français : espace fine insécable pour les milliers,
    virgule décimale et vrai signe moins. `signe` affiche aussi le « + ».
    """
    texte = f"{valeur:{'+' if signe else ''},.{decimales}f}"
    return texte.replace(",", "\u202f").replace(".", ",").replace("-", "\u2212")


def graphique(fig, **options):
    """
    Affiche une figure Plotly sur fond transparent : elle prend ainsi la
    couleur de la carte qui l'entoure, quel que soit le thème.
    """
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    if all(trace.type == "pie" for trace in fig.data):
        # Un camembert laisse de la place à droite pour une légende verticale
        fig.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.02))
    else:
        # Légende horizontale entre le titre et le graphique : une légende
        # verticale à droite prend de la largeur et se fait couper sur les
        # écrans étroits, et sous le graphique elle chevauche les étiquettes
        # inclinées de l'axe des abscisses. La marge du haut grandit avec le
        # nombre de lignes de légende (environ six entrées par ligne).
        entrees = sum(1 for trace in fig.data if trace.showlegend is not False)
        lignes = -(-entrees // 6) if entrees > 1 else 0
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                title_text="",
            ),
            margin=dict(t=70 + 24 * lignes),
            # Titre tout en haut, au-dessus de la légende
            title=dict(yref="container", y=1, yanchor="top", pad=dict(t=16)),
        )
    return st.plotly_chart(fig, **options)
