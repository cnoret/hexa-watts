"""
Streamlit Start
"""

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

## Importing pages
from content.introduction import introduction
from content.exploration import exploration
from content.preparation import preparation
from content.visualisation import visualisation
from content.modelisation import modelisation
from content.conclusion import conclusion
from content.ressources import ressources

## Page title & favicon
st.set_page_config(page_title = "Énergie France",
                   page_icon = "images/favicon.png")

## Sidebar menu
with st.sidebar:
    image_side = Image.open("images/triangle.png")
    st.image(image_side)
    st.header("L'énergie en France")
    choice = option_menu(
        menu_title = "Sommaire",
        options = ["Introduction",
                   "Exploration des données",
                   "Préparation des données",
                   "Analyses et visualisations",
                   "Modélisation et prédictions",
                   "Conclusion",
                   "Ressources"],
        default_index = 0)

    # Team
    st.header("Equipe du projet :")
    st.markdown('- Simon BERRY&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](https://www.linkedin.com/in/simon-berry56/) [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width=25>](https://github.com/sibmel29)', unsafe_allow_html=True)
    st.markdown('- Siham HOUCHI&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](https://www.linkedin.com/in/siham-houchi-19622a15a/)', unsafe_allow_html=True)
    st.markdown('- Cyril LECAILLE&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](https://www.linkedin.com/in/cyril-lecaille-8b723292/)', unsafe_allow_html=True)
    st.markdown('- Christophe NORET&nbsp;&nbsp;[<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width=25>](http://www.linkedin.com/in/cnoret) [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width=25>](https://github.com/cnoret)', unsafe_allow_html=True)

## Main Menu
if choice == "Introduction":
    introduction()

elif choice == "Exploration des données":
    exploration()

elif choice == "Préparation des données":
    preparation()

elif choice == "Analyses et visualisations":
    visualisation()

elif choice == "Modélisation et prédictions":
    modelisation()

elif choice == "Conclusion":
    conclusion()

else:
    ressources()
