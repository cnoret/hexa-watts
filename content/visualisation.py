import streamlit as st
import pandas as pd
from content.eco2mix_code import df
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt



## Color scheme qu'on va utiliser pour les grafs
colors = {
    'Thermique (MW)': 'red',
    'Nucléaire (MW)': '#F7E237',
    'Eolien (MW)': 'lightblue',
    'Solaire (MW)': 'orange',
    'Hydraulique (MW)': 'darkblue',
    'Bioénergies (MW)': 'green'
}

green = df.groupby(['Région'])[['Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Bioénergies (MW)']].sum().reset_index()

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
    
    @st.cache_data
    def create_pf2_chart(df):
        # Création d'un DataFrame regroupant la production verte/année
        green_yearly = df.groupby(['Année'])[['Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Bioénergies (MW)']].sum()
        
        # Reset the index to make 'Année' a regular column
        green_yearly = green_yearly.reset_index()

        fig = px.bar(green_yearly, x='Année', y=green_yearly.columns[1:],  # Exclude 'Année' from the y-values
            title="Évolution de la production d'énergie renouvelable par année",
            labels={'Année': 'Année', 'value': 'Production (MW)'},
            height=400, color_discrete_map=colors)

        fig.update_layout(barmode='stack')

        return fig
    
    @st.cache_data
    def create_pf3_chart(df):
        # Création d'un DataFrame regroupant la production verte/région

        fig = px.bar(green, x='Région', y=green.columns[1:], 
            title="Production d'énergie renouvelable par région",
            labels={'Région': 'Région', 'value': 'Production (MW)'},
            height=400,
            color_discrete_map=colors)  

        fig.update_layout(barmode='stack')

        return fig
    
    @st.cache_data
    def create_pf4_chart(df, type_energie):
        fig = px.pie(df, names= 'Région', values=type_energie, color_discrete_sequence=px.colors.sequential.Greens_r,
                    title=f'Répartition de la production d\'énergie {type_energie.lower()} par région')
        return fig


    ''' APRES CETTE LIMITE, ON AJOUTE TOUS LES TITRES, BODY ET APPELS DES FONCTIONS.'''
   
    st.title('1. Production de l\'énergie')

    # PF1
    pf1_chart = create_pf1_chart(production)
    st.plotly_chart(pf1_chart)
    st.info("Dépendance au nucléaire : Le graphique révèle que la France dépend largement de l'énergie nucléaire pour sa production d'électricité. Cette source d'énergie représente une part substantielle de la production totale, ce qui indique son importance dans le mix énergétique du pays. La France a historiquement investi massivement dans l'énergie nucléaire, ce qui lui a permis de disposer d'une source d'énergie fiable et à faible émission de carbone. Nous pourrons comparer cette stratégie au reste de l'Europe plus tard dans ce rapport.")

    # PF2
    pf2_chart = create_pf2_chart(production)
    st.plotly_chart(pf2_chart)
    st.info("Une tendance encourageante est l'augmentation de la part de l'énergie solaire et éolienne dans la production d'électricité au cours des dernières années. Cette croissance suggère que la France diversifie son mix énergétique en intégrant davantage d'énergies renouvelables. Les investissements dans le solaire et l'éolien reflètent une préoccupation croissante pour la réduction des émissions de gaz à effet de serre et la transition vers une production d'électricité plus propre et durable.")

    #PF3
    pf3_chart = create_pf3_chart(production)
    st.plotly_chart(pf3_chart)
    st.info("Ce graphique illustre les disparités dans les capacités de production d'énergie verte entre les différentes régions de France. Il est clairement discernable que la région Auvergne Rhône-Alpes se distingue en tant que plus grande productrice, affichant une capacité hydraulique nettement supérieure aux autres régions. Elle est suivie de près par PACA, Occitanie et le Grand Est, ce sont les régions montagneuses Le Grand Est et les Hauts-de-France se démarquent particulièrement en termes de production d'énergie éolienne.​ Sans surprise, l'énergie solaire est principalement exploitée dans les régions du sud de la France. En ce qui concerne la bioénergie, elle est mise en œuvre dans toutes les régions, et nous étudierons cet aspect de manière plus détaillée dans l'un des prochains graphiques.​")

    #PF4

    st.write("Sélectionnez un type d'énergie verte pour voir son split de production par région")
    type_energies = green.columns[1:]
    selected_energy = st.selectbox("Type d'énergie:", type_energies)

    pf4_chart = create_pf4_chart(green, selected_energy)
    st.plotly_chart(pf4_chart)

    #PF5
    st.write("Production d'énergie éolienne Offshore vs. Terrestre")

    st.image("images/PF5.png")

    st.info("Selon les données présentées dans le graphique ci-dessus, il est visible que près de 80% de l'énergie générée par l'éolien provient de parcs offshores.")

