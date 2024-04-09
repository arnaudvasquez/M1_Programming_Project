library(sf)
library(dplyr)
library(leaflet)
library(data.table)
library(rnaturalearth)
library(rnaturalearthdata)
library(tidyr)
library(htmlwidgets)

# Importation des données sur les catastrophes naturelles
gaspar <- fread("/Users/mateo/~/Desktop/Fac Strasbourg/Mémoire/Donnees_GASPAR/catnat_gaspar.csv", 
                stringsAsFactors = FALSE, sep = ';')

# Nettoyage et préparation
gaspar <- gaspar %>%
  mutate(
    date_deb = as.Date(dat_deb, format="%Y-%m-%d"),
    codecommune = as.character(cod_commune),
    lib_risque_jo = sapply(strsplit(as.character(lib_risque_jo), " "), `[`, 1)
  ) %>%
  select(lib_commune, date_deb, codecommune, lib_risque_jo)

# Télécharger la carte de la France
france <- ne_countries(scale = "medium", returnclass = "sf")
france <- france[france$admin == "France", ]

# Charger le shapefile des communes ajusté aux données
communes_sf <- st_read("~/Desktop/Fac Strasbourg/Mémoire/Traitement_final/Shapefile_communes/Shapefile traités/communes_parfait.shp")
communes_sf$codecommune <- as.character(communes_sf$codcmmn) # Assurer l'alignement des clés

# Fusionner les données GASPAR avec les données spatiales
gaspar_sf <- left_join(gaspar, communes_sf, by = "codecommune")

# Agréger les données pour compter le nombre d'occurrences par commune
catastrophes_par_commune <- gaspar_sf %>%
  group_by(codecommune) %>%
  summarise(nombre_occurrences = n()) %>%
  ungroup()

# Ajouter cette agrégation à la couche spatiale
communes_sf <- left_join(communes_sf, catastrophes_par_commune, by = "codecommune")

# Suppression des communes d'outre-mer
communes_sf <- communes_sf %>%
  filter(!grepl("^97", codecommune))

# Créer une carte interactive
map <- leaflet(communes_sf) %>%
  addProviderTiles(providers$CartoDB.Positron) %>%
  addPolygons(fillColor = ~colorQuantile("YlOrRd", nombre_occurrences, n = 5)(nombre_occurrences),
              color = "black", 
              weight = 1, 
              opacity = 1, 
              fillOpacity = 0.7,
              popup = ~paste(nom, "<br>", "Nombre de catastrophes: ", nombre_occurrences)) %>%
  addLayersControl(overlayGroups = c("Communes"),
                   options = layersControlOptions(collapsed = FALSE))

map

# Enregistrer la carte en tant que fichier HTML
saveWidget(map, '~/Desktop/Fac Strasbourg/Mémoire/Traitement_final/Map_Catastrophes.html', selfcontained = TRUE)





