import streamlit as st

def conclusion():
    st.title("Conclusion")

    st.image("images/sobriete.png", width= 300)

    st.header("\"La sobriété énergétique est la clé d'un avenir durable, car elle nous rappelle que la vraie richesse ne réside pas dans la surconsommation, mais dans l\'utilisation judicieuse des ressources de notre planète.\" - Yann Arthus-Bertrand")

    st.write("L'avenir de l'électricité en France repose sur des principes clés qui exigeront des changements majeurs pour garantir notre souveraineté énergétique d'ici 2050, notamment :\n\n"
         "- La décarbonisation de nos sources d'énergie.\n"
         "- Les avancées technologiques et scientifiques, notamment dans le stockage d'énergie par le biais de batteries. [Voir projet RINGO](https://www.rte-france.com/projets/stockage-electricite-ringo) \n"
         "- Une prise de conscience accrue de tous les acteurs de la consommation d'énergie.\n"
         "- Des actions décisives et réfléchies de la part du gouvernement.")
    
    st.warning("Il est crucial de rester vigilants face au greenwashing et aux engouements passagers. Conduire un SUV électrique, par exemple, ne garantit en aucun cas un mode de vie respectueux de nos défis énergétiques. Il est essentiel d'adopter des approches authentiques et durables pour réellement contribuer à résoudre nos problèmes énergétiques.", icon = '🚙')
