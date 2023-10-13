import streamlit as st
import pandas as pd
from content.eco2mix_code import df
import plotly.graph_objects as go


## Color scheme qu'on va utiliser pour les grafs
colors = {
    'Thermique (MW)': 'red',
    'Nucléaire (MW)': '#F7E237',
    'Eolien (MW)': 'lightblue',
    'Solaire (MW)': 'orange',
    'Hydraulique (MW)': 'darkblue',
    'Bioénergies (MW)': 'green'
}


def visualisation():
    st.title("Analyses et visualisations")

    # Création du DataFrame 'consommation'
    @st.cache_data
    def create_consommation_dataframe(df):
        to_keep = ['Région', 'Nature', 'Date', 'Heure', 'Date - Heure','Jour', 'Mois', 'Jour_mois', 'Année', 'Consommation (MW)']
        consommation = df[to_keep]
        return consommation
    consommation = create_consommation_dataframe(df)

    # Création du DataFrame 'production'
    @st.cache_data
    def create_production_dataframe(df):
        to_loose = ['Consommation (MW)']
        production = df.drop(to_loose, axis=1)
        return production
    production = create_production_dataframe(df)
    
    @st.cache_data
    def create_pf1_chart(df):
    # Notre première Data Viz PF1
        # Regroupement de la production par année de toutes les énergies
        prod = production.groupby(['Année'])[['Thermique (MW)', 'Nucléaire (MW)',
                                            'Eolien (MW)','Solaire (MW)',
                                            'Hydraulique (MW)', 'Bioénergies (MW)']].sum()

        # Calcul de la production totale
        prod_total = prod.sum(axis = 1)

        # Calcul du pourcentage de la production totale
        prod_percentage = prod.divide(prod_total, axis = 0) * 100

        # Création d'un bar chart avec plotly pour la production secteur/année
        trace_list = []
        for sector in prod_percentage.columns:
            trace = go.Bar(x = prod_percentage.index,
                        y = prod_percentage[sector],
                        name = sector,
                        marker=dict(color=colors[sector]))
            trace_list.append(trace)

        # Personnalisation du graphique
        layout = go.Layout(
            barmode = 'stack', # Barres empilées
            title = 'Production par secteur, empilée par année (% du total)',
            xaxis = dict(title = 'Année'),
            yaxis = dict(title = 'Pourcentage de la production totale'),
        )

        # Création puis affichage de la figure contenant nos 2 objets
        fig = go.Figure(data = trace_list, layout = layout)
        
        return fig
    
   
    st.title('1. Production de l\'énergie')

    # PF1
    pf1_chart = create_pf1_chart(production)
    st.plotly_chart(pf1_chart)
    st.write("Dépendance au nucléaire : Le graphique révèle que la France dépend largement de l'énergie nucléaire pour sa production d'électricité. Cette source d'énergie représente une part substantielle de la production totale, ce qui indique son importance dans le mix énergétique du pays. La France a historiquement investi massivement dans l'énergie nucléaire, ce qui lui a permis de disposer d'une source d'énergie fiable et à faible émission de carbone. Nous pourrons comparer cette stratégie au reste de l'Europe plus tard dans ce rapport.")

