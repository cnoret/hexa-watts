"""
Commentaires détaillés de la page Analyses, affichés dans les blocs « En détail ».

Ils décrivent toute la période étudiée (2013-2021), quels que soient les filtres
choisis dans la barre latérale.
"""

DETAILS = {
    "pf1": (
        "Le graphique révèle que la France dépend largement de l'énergie nucléaire pour sa "
        "production d'électricité. Cette source d'énergie représente une part substantielle "
        'de la production totale, ce qui indique son importance dans le mix énergétique du '
        "pays. La France a historiquement investi massivement dans l'énergie nucléaire, ce "
        "qui lui a permis de disposer d'une source d'énergie fiable et à faible émission de "
        "carbone. Nous pourrons comparer cette stratégie au reste de l'Europe plus tard dans "
        'ce rapport.'
    ),
    "pf2": (
        "La production d'électricité renouvelable progresse, portée par l'éolien et le "
        'solaire : la production éolienne passe de 16 TWh en 2013 à 40 TWh en 2020 (36 TWh en'
        ' 2021), et la production solaire de 4,5 à 14 TWh. À elles deux, ces filières passent'
        " de moins de 4 % à près de 10 % de la production d'électricité du pays. "
        "L'hydraulique reste la première source renouvelable, avec 53 à 75 TWh par an selon "
        "la pluviométrie : c'est elle qui fait varier le total d'une année sur l'autre. Cette"
        ' croissance montre que la France diversifie son mix électrique, dans une logique de '
        'réduction des émissions de gaz à effet de serre.'
    ),
    "pf3": (
        "Ce graphique illustre les disparités de production d'électricité renouvelable entre "
        'les régions, en cumul de 2013 à 2021. Auvergne-Rhône-Alpes se distingue nettement '
        '(environ 280 TWh), grâce à une production hydraulique bien supérieure à celle des '
        "autres régions. Elle est suivie, loin derrière, par l'Occitanie (environ 155 TWh) et"
        " le Grand Est (environ 140 TWh), puis par Provence-Alpes-Côte d'Azur (environ 110 "
        "TWh) : dans ces trois régions aussi, l'hydraulique domine, grâce aux Pyrénées, au "
        "Rhin et aux Alpes. Le Grand Est et les Hauts-de-France se démarquent pour l'éolien, "
        'dont ils assurent à eux deux près de la moitié de la production. Sans surprise, le '
        "solaire est surtout exploité dans le sud : la Nouvelle-Aquitaine, l'Occitanie et "
        "Provence-Alpes-Côte d'Azur en produisent près des deux tiers. Enfin, la bioénergie "
        'est présente dans toutes les régions.'
    ),
    "pf5": (
        'Sur la période étudiée (2013-2021), toute la production éolienne française est '
        "terrestre : le premier parc éolien en mer, au large de Saint-Nazaire, n'a été mis en"
        " service qu'en 2022. Les colonnes « Eolien terrestre » et « Eolien offshore » du jeu"
        " Eco2Mix ne sont remplies qu'en 2021, et leurs valeurs ne correspondent pas à de "
        "l'éolien : la colonne « offshore » n'est non nulle que dans les sept régions qui ont"
        " des centrales nucléaires, y compris Auvergne-Rhône-Alpes, qui n'a pas de façade "
        'maritime. Ces colonnes sont décalées par rapport à leur intitulé, et nous ne les '
        'utilisons donc pas.'
    ),
    "pf6": (
        "Sur ce graphique, nous observons les régions qui produisent de l'électricité dans "
        'des centrales nucléaires. Seules sept régions sont concernées, et Auvergne-Rhône-'
        'Alpes, le Grand Est et le Centre-Val de Loire en sont les principales productrices, '
        'avec 650 à 750 TWh chacune sur la période. Comme le nucléaire représente entre 67 % '
        "et 77 % de la production d'électricité française selon les années, toutes les "
        "régions en dépendent, y compris celles qui n'en produisent pas et qui l'importent. "
        'La partie « Distribution » montre que cinq de ces sept régions (Auvergne-Rhône-'
        'Alpes, Centre-Val de Loire, Grand Est, Normandie et Nouvelle-Aquitaine) sont '
        "exportatrices nettes chaque année de 2013 à 2020. L'Occitanie reste importatrice, et"
        " les Hauts-de-France ne deviennent exportateurs qu'à partir de 2018."
    ),
    "tcf1": (
        "Ce graphique affiche les moyennes des taux de charge pour l'énergie solaire, mettant"
        " en évidence des pics naturels pendant les mois estivaux, lorsque l'ensoleillement "
        'est plus intense. La moyenne maximale se situe aux alentours de 50%. Ce qui ressort '
        "de cette analyse, c'est que les régions générant la plus grande quantité d'énergie "
        "solaire ont généralement des taux de charge moyens plus bas. Ceci s'explique par la "
        "plus grande taille de leurs installations par rapport à d'autres régions. Par "
        "exemple, la région Centre-Val de Loire ne contribue qu'à 3 % de la production "
        'solaire totale, mais elle détient le record du taux de charge moyen, près de 50 % en'
        ' juillet.'
    ),
    "tcf2": (
        'Ce graphique illustre le taux de charge éolien, mettant en évidence des pics pendant'
        ' la saison hivernale. On observe un taux de charge moyen record pour les régions '
        'Grand Est et Centre, dépassant les 50% en février. Ces deux régions contribuent '
        'respectivement à 22% et 8% de la production éolienne en France. En revanche, la '
        'région Hauts-de-France, qui représente près de 26 % de la production éolienne '
        'totale, affiche un taux de charge moyen maximal un peu plus bas, autour de 49 %, ce '
        "qui s'explique également par la taille de ses installations."
    ),
    "tcf3": (
        "Nous choisissons ici d'observer les variations du taux de couverture du nucléaire, "
        "pour observer les différences des tendances entre les régions au cours de l'année. "
        "Ce que nous pouvons voir très clairement, c'est que la région Centre Val de Loire se"
        " démarque tout particulièrement, car c'est une région fortement productrice, mais "
        'peu consommatrice, et son taux de couverture est largement au-dessus de 100% lorsque'
        ' la consommation est moins forte dans cette région.'
    ),
    "pcf1": (
        "Ce nuage de points compare la production et la consommation d'électricité de chaque "
        'région, cumulées de 2013 à 2021. Auvergne-Rhône-Alpes est la première productrice '
        "(environ 1 050 TWh) et l'une des deux plus grosses consommatrices (environ 590 TWh)."
        " Le Grand Est, le Centre-Val de Loire et la Normandie produisent bien plus qu'ils ne"
        ' consomment : le Centre-Val de Loire produit environ quatre fois sa consommation. À '
        "l'inverse, la Bourgogne-Franche-Comté, la Bretagne et les Pays de la Loire ne "
        "produisent que 15 à 25 % environ de ce qu'ils consomment, et l'Île-de-France, "
        'première consommatrice (environ 635 TWh), à peine 5 %. Ces régions dépendent des '
        'échanges avec les régions productrices.'
    ),
    "df1": (
        'La carte montre le solde des échanges de chaque région, année par année : en rouge '
        'les régions importatrices, en bleu les exportatrices. Les tendances restent stables '
        'de 2013 à 2020, à deux nuances près : les exportations nettes de la Normandie '
        'diminuent de plus de moitié (49 TWh en 2013, 21 TWh en 2020), et les Hauts-de-France'
        " passent d'importateurs à exportateurs nets à partir de 2018. Les échanges de 2021 "
        'ne sont pas exploitables dans notre jeu de données.'
    ),
    "pe1a": (
        "Le graphique montre la production d'énergies renouvelables cumulée de 2013 à 2021, "
        "toutes formes d'énergie confondues (pas seulement l'électricité). L'Allemagne est en"
        " tête (environ 9 900 TWh), suivie de la France et de l'Italie presque à égalité "
        '(environ 5 700 et 5 600 TWh), puis de la Suède (environ 4 200 TWh). Les facteurs '
        'influençant ces résultats incluent les ressources naturelles, les politiques '
        'gouvernementales, les investissements dans les technologies écologiques, ainsi que '
        "la taille et la consommation énergétique des pays. En Allemagne, l'accent est mis "
        "sur l'éolien, le solaire photovoltaïque et la biomasse grâce à l'initiative "
        'Energiewende. La France, bien que dépendante du nucléaire, cherche à diversifier son'
        ' mix énergétique en favorisant les énergies renouvelables, en particulier '
        "l'hydroélectricité. L'Italie se distingue par son potentiel en énergie solaire "
        "photovoltaïque, tandis que la Suède mise sur l'hydroélectricité et la bioénergie "
        "pour atteindre une production énergétique 100% renouvelable d'ici 2040. L'Allemagne "
        'et la France se démarquent également dans les biocarburants et la bioénergie, grâce '
        'à des politiques favorables, des ressources agricoles abondantes et des incitations '
        "financières pour la production d'énergie à partir de résidus organiques."
    ),
    "pe2a": (
        "De 2013 à 2021, la production européenne d'énergie renouvelable progresse surtout, "
        'en volume, grâce aux biocarburants (+585 TWh), à la bioénergie (+208 TWh) et à '
        "l'éolien (+177 TWh). En proportion, les plus fortes hausses sont celles des pompes à"
        ' chaleur (production multipliée par 3,2), du solaire photovoltaïque (multipliée par '
        "2) et de l'éolien (multipliée par 1,85). L'hydraulique, elle, recule légèrement."
    ),
    "ce3": (
        "La consommation d'énergies renouvelables en Europe connaît une croissance "
        'significative, stimulée par des politiques environnementales strictes, des objectifs'
        ' de réduction des émissions et des incitations financières. Les biocarburants '
        'gagnent en popularité pour diversifier les transports, tandis que la bioénergie '
        "prospère grâce aux ressources forestières et agricoles abondantes. L'énergie "
        'hydraulique et éolienne est privilégiée dans des régions adaptées, tandis que le '
        'biogaz et les déchets municipaux renouvelables sont encouragés pour une gestion '
        'durable des déchets. Les pompes à chaleur, le solaire, et la géothermie sont '
        "préférés en fonction des ressources locales, tandis que l'énergie océanique est "
        'encore en développement.'
    ),
}
