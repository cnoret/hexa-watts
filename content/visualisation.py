import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from datetime import datetime as dt
import pyarrow.parquet as pq


## Color scheme qu'on va utiliser pour les grafs
colors = {
    'Thermique (MW)': 'red',
    'Nucléaire (MW)': '#F7E237',
    'Eolien (MW)': 'lightblue',
    'Solaire (MW)': 'orange',
    'Hydraulique (MW)': 'darkblue',
    'Bioénergies (MW)': 'green'
}

# Pour les données Europe aussi
colors_euro = {
    'Bioénergie': '#FF0000',  # Rouge
    'Déchets municipaux renouvelables': '#00FF00',  # Vert
    'Éolien': '#ADD8E6',  # Bleu clair
    'Solaire Photovoltaique': '#FFA500',  # Orange
    'Solaire Thermique': '#FFFF00',  # Jaune
    'Hydraulique': '#00008B',  # Bleu foncé
    'Biogaz': '#808080',  # Gris
    'Biocarburants': '#800080',  # Violet
    'Pompe à chaleur': '#FF0000',  # Rouge
    'Océan': '#0000FF',  # Bleu
    'Geothermique': '#D076FF'  # Violet
}

EUROPE_DATA = pd.read_csv('datasets/EUROPE_DATA.csv', sep = ',')

def visualisation():

    table = pq.read_table('datasets/df_modified.parquet')
    df = table.to_pandas()

    green = df.groupby(['Région'])[['Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Bioénergies (MW)']].sum().reset_index()

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

        # Création du DataFrame 'EUROPE_PROD'
    @st.cache_data
    def create_prod_europe(df):
        EUROPE_PROD = EUROPE_DATA[EUROPE_DATA['Type'] == 'Production']
        return EUROPE_PROD
    EUROPE_PROD = create_prod_europe(EUROPE_DATA)

        # Création du DatFrame 'EUROPE_CONS'
    @st.cache_data
    def create_cons_europe(df):
        EUROPE_CONS = EUROPE_DATA[EUROPE_DATA['Type'] == 'Consommation']
        return EUROPE_CONS
    EUROPE_CONS = create_cons_europe(EUROPE_DATA)

    def create_pe1a_chart(df):
        EUROPE_PROD_TYPE = EUROPE_PROD.groupby(['Pays', 'Class'])['Valeur (MW)'].sum().reset_index()
        fig = px.bar(
        EUROPE_PROD_TYPE,
        x = 'Pays',
        y = 'Valeur (MW)',
        color = 'Class',
        labels = {'Valeur (MW)': 'Production totale', 'Pays': 'Pays'},
        title = 'Production totale par pays en énergie renouvelable'
         )

        for classification, color in colors_euro.items():

            fig.update_traces(marker_color=color, selector=dict(name=classification))
        
        return fig
    
    def create_pe2a_chart(df):
        euro_yearly = EUROPE_PROD.groupby(["Class", "Année"])["Valeur (MW)"].sum().unstack().transpose()
        fig = px.bar(euro_yearly,
             x = euro_yearly.index, y = euro_yearly.columns,
             title = "Totaux Européens en production par type d'énergie renouvelable",
             labels = {"x": "Année", "y": "Valeur (MW)"})
        fig.update_layout(barmode = 'stack',
                        xaxis_title = "Année", yaxis_title = "Valeurs",
                        legend_title = "Classification")

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig
    
    #Variables pour df1 & df2
    distrib_col = ['Région', 'Année', 'Ech. physiques (MW)']
    distrib = df[distrib_col].groupby(['Région', 'Année'])['Ech. physiques (MW)'].sum().reset_index()
    distrib = distrib[distrib['Année'] != 2021] # On ne veux pas de 2021 dans cette étude
    
    def create_df1_chart(df, region):
        #Normalisation pour meilleur représentation visuelle.
        scaler = StandardScaler()
        distrib["Ech. physiques (MW)"] = scaler.fit_transform(distrib["Ech. physiques (MW)"].values.reshape(-1, 1))

        #Plot
        plt.figure(figsize=(10, 6))
        region_data = distrib[distrib["Région"] == region]
        plt.plot(region_data["Année"], region_data["Ech. physiques (MW)"], marker='o')
        plt.title(f"Progression annuelle des échanges physiques en {region}")
        plt.xlabel("Année")
        plt.ylabel("Ech. physiques (MW)")
        plt.grid(True)
        st.pyplot(plt) 

    #TCO & TCH
    # Liste contenant les mois dans l'ordre chronologique pour plotly
    month_order = ['January', 'February', 'March', 'April',
               'May', 'June', 'July', 'August', 'September',
               'October', 'November', 'December']

    tco_tch_table = pq.read_table('datasets/tco_tch.parquet')
    tco_tch = tco_tch_table.to_pandas()

    # Création d'un Dataframe groupé pour analyse des Taux de charge solaire
    tco_tch_grouped_solaire = tco_tch.groupby(['Région', 'Mois'])['TCH Solaire (%)'].mean().reset_index()
    tco_tch_grouped_solaire['Mois'] = pd.Categorical(tco_tch_grouped_solaire['Mois'],
                                                    categories = month_order,
                                                    ordered = True)
    tco_tch_grouped_solaire = tco_tch_grouped_solaire.sort_values(by = 'Mois')

    # Création d'un Dataframe groupé pour analyse des Taux de charge éolien
    tco_tch_grouped_eolien = tco_tch.groupby(['Région', 'Mois'])['TCH Eolien (%)'].mean().reset_index()
    tco_tch_grouped_eolien['Mois'] = pd.Categorical(tco_tch_grouped_eolien['Mois'],
                                                    categories = month_order,
                                                    ordered = True)
    tco_tch_grouped_eolien = tco_tch_grouped_eolien.sort_values(by = 'Mois')

    # Création d'un Dataframe groupé pour analyse des Taux de couverture nucléaire
    tco_nuke = tco_tch.groupby(['Région', 'Mois'])['TCO Nucléaire (%)'].mean().reset_index()
    tco_nuke['Mois'] = pd.Categorical(tco_nuke['Mois'], categories = month_order,
                                    ordered = True)
    tco_nuke = tco_nuke.sort_values(by = 'Mois')

    def create_tcf1_chart(df):
        fig = px.line(
        tco_tch_grouped_solaire,
        x = 'Mois',
        y = 'TCH Solaire (%)',
        color = 'Région',
        title = 'TCH Solaire (%) par Mois et Région'
        )

        # Titres
        fig.update_layout(
            xaxis_title = 'Mois',
            yaxis_title = 'TCH Solaire (%)',
            legend_title = 'Région',
        )

        return fig
    
    def create_tcf2_chart(df):
        fig = px.line(
        tco_tch_grouped_eolien,
        x = 'Mois',
        y = 'TCH Eolien (%)',
        color = 'Région',
        title = 'TCH Eolien (%) par Mois et Région'
        )

        # Titres
        fig.update_layout(
        xaxis_title = 'Mois',
        yaxis_title = 'TCH Eolien (%)',
        legend_title = 'Région',
        )

        return fig
    
    def create_tcf3_chart(df):
        fig = px.line(
        tco_nuke,
        x = 'Mois',
        y = 'TCO Nucléaire (%)',
        color = 'Région',
        title = 'TCO Nucléaire (%) par Mois et Région'
        )

        # Titres
        fig.update_layout(
        xaxis_title = 'Mois',
        yaxis_title = 'TCO Nucléaire %',
        legend_title = 'Région',
        )

        return fig
    
    daily_total_year = consommation.groupby(['Heure', 'Année'])['Consommation (MW)'].mean()
    df_daily = pd.DataFrame(daily_total_year).reset_index()

    def create_cf4_chart(df):
        fig = px.line(df_daily,
              x = 'Heure', y = 'Consommation (MW)',
              color = 'Année', hover_data = ['Année'])
        fig.update_layout(title='Consommation dans une journée type, par année')
        return fig

    def create_pcf1_chart(df):
        # Création d'un dataset qui reprends les deux données cibles pour chaque région
        consprod = df.groupby(['Région'])[['Consommation (MW)', 'Production (MW)']].sum().reset_index()

        # Création d'une visualisation Plotly scatter pour comparer les régions entre elles
        fig = px.scatter(consprod,
                        x = 'Production (MW)', y = 'Consommation (MW)',
                        color = 'Région',
                        title = 'Production VS Consommation par région',
                        labels = {'Production (MW)': 'Production', 'Consommation (MW)': 'Consommation'},
                        hover_data = ['Région'],
                        size='Production (MW)',
                        size_max=30)

        # Personnalisation du graphique
        fig.update_layout(
            xaxis_title = 'Production (MW)',
            yaxis_title = 'Consommation (MW)',
            legend_title = 'Régions',
            xaxis = dict(gridcolor = 'lightgray'),
            yaxis = dict(gridcolor = 'lightgray'),
        )

        return fig
    
    def create_ce3_chart(df):

        EUROPE_CONS_TYPE = EUROPE_CONS.groupby(['Pays', 'Class'])['Valeur (MW)'].sum().reset_index()

        fig = px.bar(
            EUROPE_CONS_TYPE,
            x = 'Pays',
            y = 'Valeur (MW)',
            color = 'Class',
            labels = {'Valeur (MW)': 'Consommation totale', 'Pays': 'Pays'},
            title = 'Consommation totale par pays d\'énergies renouvelables'
        )

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color=color, selector=dict(name=classification))

        return fig 
    
    def create_ce4_chart(df):
        ## Graphique CE4
        ## Total consommation annuelle  d'énergie renouvelable en Europe par type d'énergie

        # Grouper les données par "Classification" et "Année" et calculer la somme de la consommation
        euro_yearly = EUROPE_CONS.groupby(["Class", "Année"])["Valeur (MW)"].sum().unstack()

        euro_yearly = euro_yearly.transpose()

        # Création plotly
        fig = px.bar(euro_yearly, x = euro_yearly.index, y = euro_yearly.columns,
                    title = "Totaux Européens en consommation d'énergies renouvelables",
                    labels = {"x": "Année", "y": "Valeur (MW)"})
        fig.update_layout(barmode = 'stack', xaxis_title = "Année",
                        yaxis_title = "Valeurs", legend_title = "Classification")

        for classification, color in colors_euro.items():
            fig.update_traces(marker_color = color, selector = dict(name = classification))

        return fig



    ''' APRES CETTE LIMITE, ON AJOUTE TOUS LES TITRES, BODY ET APPELS DES FONCTIONS.'''
   
    ### PRODUCTION ###
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

    st.warning("Sélectionnez un type d'énergie verte pour voir son split de production par région", icon= "🤖")
    type_energies = green.columns[1:]
    selected_energy = st.selectbox("Type d'énergie:", type_energies)

    pf4_chart = create_pf4_chart(green, selected_energy)
    st.plotly_chart(pf4_chart)

    #PF5
    st.write("Production d'énergie éolienne Offshore vs. Terrestre")

    st.image("images/PF5.png")

    st.info("Selon les données présentées dans le graphique ci-dessus, il est visible que près de 80% de l'énergie générée par l'éolien provient de parcs offshores.")

    #PF6
    st.write("Production d'énergie éolienne Offshore vs. Terrestre")

    st.image("images/PF6.png")

    st.info("Sur ce graphique, nous observons les diverses régions qui génèrent de l'énergie à partir de leurs centrales nucléaires.​Il est notable que seules sept régions sont impliquées dans la production de cette forme d'énergie, avec l'Auvergne, le Grand Est et la région Centre se distinguant comme les principaux acteurs.​ Toutefois, en raison de la prédominance de l'énergie nucléaire dans la stratégie énergétique de la France, qui représente environ 70 % de sa production totale, toutes les régions du pays sont dépendantes de cette source d'énergie et en importent.​ Comme nous allons pouvoir le voir dans la partie 'Distribution' les balances d'exportation d'énergie des régions produisant du nucléaire sont toujours excédentaires.")

    st.title("Focus sur TCO & TCH")
    st.info("Le taux de charge d'une filière se réfère à la quantité de production par rapport à la capacité de production totale en service de cette filière.", icon= "ℹ️")
    
    tcf1_chart = create_tcf1_chart(tco_tch)
    st.plotly_chart(tcf1_chart)
    st.write("Le graphique présent affiche les moyennes des taux de charge pour l'énergie solaire, mettant en évidence des pics naturels pendant les mois estivaux, lorsque l'ensoleillement est plus intense. La moyenne maximale se situe aux alentours de 50%. Ce qui ressort de cette analyse, c'est que les régions générant la plus grande quantité d'énergie solaire ont généralement des taux de charge moyens plus bas. Ceci s'explique par la plus grande taille de leurs installations par rapport à d'autres régions. Par exemple, la région Centre ne contribue qu'à 3% de la production d'énergie solaire totale, mais en juillet, elle détient le record du taux de charge, dépassant les 50%.")
    
    tcf2_chart = create_tcf2_chart(tco_tch)
    st.plotly_chart(tcf2_chart)
    st.write("Le graphique ci-dessous illustre le taux de charge éolien, mettant en évidence des pics pendant la saison hivernale. On observe un taux de charge moyen record pour les régions Grand Est et Centre, dépassant les 50% en février. Ces deux régions contribuent respectivement à 22% et 8% de la production éolienne en France. En revanche, la région Hauts-de-France, qui représente près de 26% de la production éolienne totale, affiche une moyenne de taux de charge maximale de 46%, ce qui s'explique également par la taille de ses installations.")

    st.info("Le taux de couverture d’une filière de production au sein d’une région représente la part de cette filière dans la consommation de cette région.", icon= "ℹ️")
    tcf3_chart = create_tcf3_chart(tco_tch)
    st.plotly_chart(tcf3_chart)
    st.write("Nous choisissons ici d'observer les variations du taux de couverture du nucléaire, pour observer les différences des tendances entre les régions au cours de l'année.​ Ce que nous pouvons voir très clairement, c'est que la région Centre Val de Loire se démarque tout particulièrement, car c'est une région fortement productrice, mais peu consommatrice, et son taux de couverture est largement au-dessus de 100% lorsque la consommation est moins forte dans cette région.​")

    st.header('Donnée de la production des Pays Européens')

    pe1a_chart = create_pe1a_chart(EUROPE_PROD)
    st.plotly_chart(pe1a_chart)
    st.info("Le graphique PE1a montre la production d'énergies renouvelables en Europe, avec l'Allemagne en tête, suivie de la France et de l'Italie à égalité en deuxième position, et la Suède en troisième. Les facteurs influençant ces résultats incluent les ressources naturelles, les politiques gouvernementales, les investissements dans les technologies écologiques, ainsi que la taille et la consommation énergétique des pays. En Allemagne, l'accent est mis sur l'éolien, le solaire photovoltaïque et la biomasse grâce à l'initiative Energiewende. La France, bien que dépendante du nucléaire, cherche à diversifier son mix énergétique en favorisant les énergies renouvelables, en particulier l'hydroélectricité. L'Italie se distingue par son potentiel en énergie solaire photovoltaïque, tandis que la Suède mise sur l'hydroélectricité et la bioénergie pour atteindre une production énergétique 100% renouvelable d'ici 2040. L'Allemagne et la France se démarquent également dans les biocarburants et la bioénergie, grâce à des politiques favorables, des ressources agricoles abondantes et des incitations financières pour la production d'énergie à partir de résidus organiques.")

    pe2a_chart = create_pe2a_chart(EUROPE_PROD)
    st.plotly_chart(pe2a_chart)
    st.info("L'augmentation annuelle la plus marquée est celle des énergies suivantes: énergies renouvelables, telles que les biocarburants, les pompes à chaleur, le solaire photovoltaïque et l'éolien.")


    st.title("Distribution de l'énergie")

    st.warning("Sélectionnez une région pour afficher le graphique", icon= "🤖")
    regions = distrib["Région"].unique()
    selected_region = st.selectbox("Région", regions)
    create_df1_chart(distrib, selected_region)

    st.image("images/distrib_map.png")
    st.info("La carte de France nous montre en rouge les régions les plus importatrices, et en bleu les plus exporatrices. Les tendances restent très stables de 2013 à 2021.")
    
    ### CONSOMMATION ###
    
    st.title("Consommation de l'énergie")
    # CF1
    st.image("images/CF1.png")
    st.write("")

    # CF2
    st.image("images/CF2.png")
    st.write("")
    
    # CF3
    st.image("images/CF3.png")
    st.write("")

    # CF4
    
    cf4_chart = create_cf4_chart(consommation)
    st.plotly_chart(cf4_chart)
    
    # CF5 &/ou 6

    # CF7
    
    st.header("Focus sur la population, ajout des données de l'INSEE.")
    st.info('Nous avons créé un ratio "Consommation Per Capita" pour comparer les régions entres elles. Consommation Totale / Nombre d\'habitants', icon = "🏘️")
    st.image("images/CF7.png")
    st.write("Nous observons que les régions du sud ont historiquement toujours eu un consommation Per Capita plus élevée que celles du Nord, mais depuis 2021 cette tendence s'est inversée.")

    # CF8 / 9 / 11

    st.title('Comparaison de la production et de la consommation de l\'énergie')

    pcf1_chart = create_pcf1_chart(df)
    st.plotly_chart(pcf1_chart)
    st.write("Ce graphique Scatterplot Plotly compare la production totale d'énergie ('Production (MW)') avec la consommation d'énergie ('Consommation (MW)') dans différentes régions. Il révèle que la région Auvergne-Rhône-Alpes est la principale productrice et consommatrice d'énergie. Le Grand Est est un bon producteur avec une consommation relativement plus faible. Le Centre-Val de Loire semble exporter de l'énergie, tandis que les régions Pays de la Loire, Bretagne et Bourgogne gèrent efficacement leur consommation. Enfin, l'Île-de-France se distingue par sa forte consommation et une contribution minimale à la production. Ce graphique met en lumière les disparités régionales en matière d'énergie.")

    st.header("La sobriété énergétique")
    st.info("Le secteur de l'électricité en France implique plusieurs acteurs clés, notamment RTE pour le transport, Enedis pour la distribution, et EDF pour la production. Dans les données d'Enedis Open Data pour 2022 et 2023, trois catégories de consommateurs sont distinguées : résidentiels, professionnels, et entreprises, avec des économies d'énergie lors de températures plus élevées l'hiver.")
    st.image("images/PCF2.png")
    st.info("La différence entre les résidentiels et les entreprises/professionnels, peut s'expliquer par la nature de leur comportement en terme de dépenses énergétiques: En effet, les résidentiels ont des habitudes plus réactive (Je baisse, j'augmente) alors que les entreprises et les professionnels sont plutôt proactifs, et ne touchent bien souvent pas au thermostat pour rester stable.​")

    st.title("Consommation des énergies renouvelables en Europe")

    st.image("images/CE1.png")

    st.image("images/CE2.png")
    st.write("La consommation d'énergies renouvelables en Europe connaît une croissance significative, stimulée par des politiques environnementales strictes, des objectifs de réduction des émissions et des incitations financières. Les biocarburants gagnent en popularité pour diversifier les transports, tandis que la bioénergie prospère grâce aux ressources forestières et agricoles abondantes. L'énergie hydraulique et éolienne est privilégiée dans des régions adaptées, tandis que le biogaz et les déchets municipaux renouvelables sont encouragés pour une gestion durable des déchets. Les pompes à chaleur, le solaire, et la géothermie sont préférés en fonction des ressources locales, tandis que l'énergie océanique est encore en développement.")

    ce3_chart = create_ce3_chart(EUROPE_CONS)
    st.plotly_chart(ce3_chart)
    st.info("PLACEHOLDER")

    ce4_chart = create_ce4_chart(EUROPE_CONS)
    st.plotly_chart(ce4_chart)
    st.info("PLACEHOLDER")

    ## Graphique CE5
    ## Consommation d'énergie renouvelable par catégorie d'énergie (Exemple Allemagne)

    # Création d'un sous-ensemble de données pour les années de 2013 à 2021
    years_to_include = list(range(2013, 2022))
    df_subset = EUROPE_CONS[EUROPE_CONS['Année'].isin(years_to_include)]

    # Regroupement des données par "Pays" et "Classification" et calcul de la somme de la consommation
    euro_type = df_subset.groupby(['Pays', 'Class'])['Valeur (MW)'].sum().reset_index()

    # Convertion de la colonne "Valeurs" en type de données décimales (float)
    euro_type['Valeur (MW)'] = euro_type['Valeur (MW)'].astype(float)

    # Calcul de la consommation totale par pays
    total_consommation_by_country = euro_type.groupby('Pays')['Valeur (MW)'].sum()

    # Création d'un dictionnaire de données pour le graphique à secteurs de chaque pays
    data_for_pie_charts = {}
    for country, group in euro_type.groupby('Pays'):
        # Calcul de la consommation par type d'énergie pour ce pays
        group['Pourcentage'] = (group['Valeur (MW)'] / total_consommation_by_country[country]) * 100
        data_for_pie_charts[country] = group.set_index('Class')['Pourcentage']

    countries = euro_type['Pays'].unique()

    # Widget
    st.info("Selectionnez un pays", icon = "🇪🇺")
    pays = st.selectbox(countries)
    donnees = data_for_pie_charts[pays]

    ce5 = go.Figure(data=[go.Pie(labels=donnees.index, values=donnees.values, textinfo='percent+label')])

    ce5.update_layout(
            title=f"Pourcentage de la consommation d'énergie renouvelable en {pays} (2013-2021)",
            legend_title="Catégorie",
    )
    st.plotly_chart(ce5)
    