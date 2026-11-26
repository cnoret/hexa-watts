"""
Creation of the "Conclusion" page for the Hexa Watts application
"""

import streamlit as st

from content.interface import en_tete

# Les images sont passées à st.image par leur chemin : Streamlit lit le fichier
# à chaque affichage. Un objet PIL mis en cache avec st.cache_resource serait
# partagé entre les sessions, et deux lectures simultanées du même fichier
# provoquent l'erreur « image file is truncated ».


def conclusion():
    """Content of the conclusion page"""
    # Title and Key Quote
    en_tete(
        "Conclusion",
        surtitre="Étape 5 · Ce que nous retenons",
        sous_titre="Les défis du système électrique français d'ici 2050.",
    )

    st.markdown(
        """
        > **\"La sobriété énergétique est la clé d'un avenir durable, car elle nous rappelle que la vraie richesse ne réside pas dans la surconsommation, mais dans l'utilisation judicieuse des ressources de notre planète.\"**
        >
        > — Yann Arthus-Bertrand
        """
    )

    st.divider()

    # Key Insights
    st.subheader("Les défis à relever pour 2050")
    st.markdown(
        """
        - **Décarbonation** des sources d'énergie.
        - **Avancées technologiques**, notamment dans le stockage d'énergie via des batteries. [Voir projet RINGO](https://www.rte-france.com/projets/stockage-electricite-ringo)
        - **Sensibilisation accrue** des citoyens et des entreprises aux enjeux énergétiques.
        - **Décisions stratégiques** du gouvernement pour une transition réfléchie.
        """
    )

    # Warnings in Columns
    col1, col2 = st.columns(2)
    with col1:
        st.warning(
            """
            **⚠️ Vigilance face au greenwashing**
            - Adoptez des comportements réellement respectueux de l'environnement.
            - Conduire un SUV électrique, par exemple, ne garantit pas un mode de vie durable.
            """
        )
    with col2:
        st.warning(
            """
            **⚠️ Dépendance au nucléaire**
            - Fragilité face aux risques géopolitiques.
            - Exemple : Guerre en Ukraine ou coup d'État au Niger affectant l'approvisionnement.
            """
        )

    st.divider()

    # Africa and Hydrogen Section
    st.subheader("L'Afrique et l'hydrogène : un avenir prometteur")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(
            """
            L'hydrogène 'H2', l'élément chimique le plus répandu dans l'univers, représente une solution clé :
            - **Déjà utilisé** pour alimenter des transports énergivores.
            - **Projets prometteurs** en Namibie et dans d'autres régions africaines pour produire de l'hydrogène vert.
            - **Impact global** : Capacité de répondre à la demande mondiale tout en réduisant les émissions carbone.
            """
        )
    with col2:
        try:
            st.image(
                "images/africa_hydrogen.png",
                width="stretch",
            )
        except FileNotFoundError:
            st.warning("Image introuvable : vérifiez le chemin ou le fichier.")

    st.divider()

    # Additional Resources
    st.subheader("Ressources supplémentaires")
    st.markdown(
        """
        - [Agence Internationale de l'Énergie](https://www.iea.org/)
        - [Projet RINGO de RTE](https://www.rte-france.com/projets/stockage-electricite-ringo)
        - [Namibia Hydrogen Power Projects](https://www.namcor.com.na/)
        """
    )

    st.info(
        """
        **Conclusion finale** : La sobriété énergétique, combinée à des avancées technologiques,
        une gestion stratégique et une coopération internationale, est essentielle pour relever les défis énergétiques de demain.
        """,
        icon=":material/lightbulb:",
    )
