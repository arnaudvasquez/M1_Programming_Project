# M1_Programming_Project

Le but de notre projet est d’automatiser quotidiennement le téléchargement des bases de données GASPAR, notamment celle recensant les catastrophes naturelles par commune, puis de générer une carte quotidienne sur ces catastrophes. Dans un second temps nous avons automatisé la récupération d’articles de presse sur ces catastrophes afin de mener une analyse de sentiment, pour estimer la manière dont réagit la presse à ces catastrophes naturelles. 

Notre projet présente les différents codes suivants : 
- Téléchargement_quotidien_GASPAR : permet de télécharger automatiquement la base de données GASPAR
- Carte : génère une carte interactive des catastrophes naturelles par commune
- Presse_scraping : permet de récupérer automatiquement les articles de presse en liens avec les catastrophes naturelles
- CAPTCHA_solving : permet d'automatiser le passage d'une CAPTCHA (dans le cas de Presse_scraping)
- Sentiment_analysis : effectue une analyse de sentiments sur les articles de presse téléchargées précédemment 
