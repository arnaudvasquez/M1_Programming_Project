#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 01:47:39 2024

@author: mateo
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import os
import re

# Chargement du fichier contenant l'ensemble des catastrophes naturelles en France depuis un bon bout de temps
# Les informations principales sont la localisation de la catastrophe, son type et sa date.
chemin_fichier = '/Users/mateo/~/Desktop/Fac Strasbourg/Mémoire/Donnees_GASPAR/catnat_gaspar.csv'
df = pd.read_csv(chemin_fichier, sep=';')

# Nous choisissons Firefox pour des raisons liées à la CAPTCHA 
driver = webdriver.Firefox()

# Accéder à la page de la BU Unistra directement sur le lien permettant d'accéder à Factiva 
driver.get("https://bu.unistra.fr/opac/resource/factiva/BUS1884906?tabDoc=tabcontiene")

# Attendre que la nouvelle fenêtre soit ouverte
time.sleep(2)

# Attendre jusqu'à ce que le lien soit visible et cliquer dessus pour accéder à Factiva
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[target='new']"))
).click()

# Attendre que la nouvelle fenêtre soit ouverte
time.sleep(2)

# Une fenêtre d'identification à Ernest s'ouvre
# Pour pouvoir interagir avec les éléments de cette nouvelle fenêtre 
# il est nécessaire de dire explicitement à Selenium sur quelle fenêtre focaliser ses actions
window_after = driver.window_handles[1]
driver.switch_to.window(window_after)



# Attendre jusqu'à ce que le nom d'utilisateur, le mdp et le bouton de connexion soit présents
# avant de remplir le nom d'utilisateur et le mdp, et cliquer sur le bouton de connexion
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "username"))
).send_keys("username")


WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "password"))
).send_keys("password")


WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.ID, "login-btn"))
).click()


time.sleep(5)

# Basculer vers la fenêtre de Factiva
window_after = driver.window_handles[1]
driver.switch_to.window(window_after)

time.sleep(10)


# D'abord, nous allons affiner notre recherche en sélectionnant unique les articles publiés en France
# Le problème est le suivant : afin de sélectionner uniquement la France, nous devons dérouler
# une menu déroulant, ce qui pose plusieurs problèmes, notamment la localisation des éléments 
# sur lesquels nous devons cliquer car ces derniers sont "cachés" dans le menu déroulant 

# D'abord, nous cliquons sur Région, ce qui nous permet d'ouvrir le menu déroulant
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Région')]"))
).click()

# Puis nous cliquons sur le bouton "+" pour "Europe" ce qui nous permet d'étendre la sélection
# Le problème ici est que nous n'arrivions pas à localiser ce bouton
# Ainsi nous avons du controuner ce problème en disant à selenium de cliquer 
# l'élément de class='mnuBtn' qui est présent juste avant le texte Europe 
plus_button_xpath = "//a[contains(text(), 'Europe')]/preceding-sibling::span[@class='mnuBtn']/span"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, plus_button_xpath))
).click()



# De même, nous étendons maitnenant la section "Europe de l'Ouest" afin de voir apparaître la France
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ouest')]/preceding::span[@class='mnuBtn'][1]"))
).click()



# Et nous cliquons enfin sur "France"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'France')]"))
).click()

# Attendre un peu pour s'assurer que la section se soit bien effectuée
time.sleep(2)


# Ensuite, sachant que nous allons télécharger les articles de presse, nous devons faire en sorte 
# de pouvoir retracer les fichiers téléchargés, notamment le dernier, afin de pouvoir 
# remplacer le nom original des fichiers par le format de nom que nous avons choisi


informations_fichiers = []
dossier_telechargements = '/Users/mateo/downloads'

# Fonction pour obtenir le dernier fichier téléchargé
def obtenir_dernier_fichier(dossier_telechargements):
    liste_fichiers = [os.path.join(dossier_telechargements, f) for f in os.listdir(dossier_telechargements)]
    fichiers_valides = [f for f in liste_fichiers if os.path.isfile(f) and re.match(r'Factiva-\d{8}-\d{4}\.rtf', os.path.basename(f))]
    dernier_fichier = max(fichiers_valides, key=os.path.getctime, default=None)
    return dernier_fichier



# Nous initions ici la boucle qui va :
# - parcourir l'ensemble des lignes du df contenant les catastrophes naturelles
# - identifier la date de début puis calculer une date de fin en ajoutant 6 mois (pour indiquer que nous voulons
# uniquement chercher des articles à partir de la date de survenue de la catastrophe jusqu'à 6 mois après)
# - identifier la commune et le type de catastrophe afin d'indiquer dans la recherche 'nom_commune AND type_catastrophe'
# - lancer la recherche puis télécharger tous les articles de la première page, et passer à la page suivante
# - résoudre la CAPTCHA afin de pouvoir accéder aux téléchargements de la page suivante
# 
for index, row in df.iterrows():
    try:
        # Récupération de la date de début et calcul de la date de fin
        date_debut = pd.to_datetime(row['dat_deb'])
        date_fin = date_debut + pd.DateOffset(months=6)

        # Formatage des dates afin qu'il corresponde au format attendu, c'est-à-dire JJ/MM/AAAA
        date_debut_str = date_debut.strftime('%d%m%Y')
        date_fin_str = date_fin.strftime('%d%m%Y')

        # Sélectionner l'option "Sélectionner une période" et remplir les dates
        select_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "dr"))
        )
        Select(select_element).select_by_visible_text("Sélectionner une période...")

        # Remplir la date de début
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "frd"))
        ).send_keys(date_debut_str[:2])  # Jour
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "frm"))
        ).send_keys(date_debut_str[2:4])  # Mois
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "fry"))
        ).send_keys(date_debut_str[4:])  # Année

        # Remplir la date de fin
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "tod"))
        ).send_keys(date_fin_str[:2])  # Jour
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "tom"))
        ).send_keys(date_fin_str[2:4])  # Mois
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "toy"))
        ).send_keys(date_fin_str[4:])  # Année

        # Construction des mots-clés dynamiques avec remplacements
        mot_cle_commune = row['lib_commune'].replace('/', ' ')
        mot_cle_risque = row['lib_risque_jo'].replace('/', ' ').split()[0]
        mot_cle = f"{mot_cle_commune} and {mot_cle_risque}"
        
        # Localiser et remplir le champ de recherche
        champ_recherche = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ace_text-input"))
        )
        champ_recherche.clear()
        champ_recherche.send_keys(mot_cle)
        champ_recherche.send_keys(Keys.RETURN)

        
        # Attendre un certain temps pour que le téléchargement se termine
        time.sleep(5)
        numero_page = 1
        
        # Vérifier si le message "Aucun résultat" est présent
        try:
            aucun_resultat = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='headlines' and contains(text(), 'Aucun résultat')]"))
            )
            print(f"Aucun résultat pour la recherche à la ligne {index}. Passage à la ligne suivante.")
            
            # Retour à la page de recherche initiale
            driver.get("https://global-factiva-com.scd-rproxy.u-strasbg.fr/sb/default.aspx?lnep=hp")  # Remplacez par l'URL réelle
            
            continue  # Passe à la prochaine itération de la boucle for
        except TimeoutException:
            # Aucun message "Aucun résultat" trouvé, continuer le traitement
            pass
        
 

        numero_page = 1
        derniere_page = False

        while not derniere_page:
            
            # Sélectionner tous les articles
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"][onclick^="selectAll"]'))
            ).click()

            # Cliquer sur "Enregistrer au format RTF"
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.ppsBtn[title="Télécharger les articles en format RTF"]'))
            ).click()

            # Attendre que le menu des options d'enregistrement soit visible
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//ul[@id='listMenu-id-3' and contains(@style, 'display: block')]"))
            )

            # Sélectionner "Format article complet"
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, \"viewProcessing('../pps/default.aspx?pp=RTF&ppstype=Article',true);\")]"))
            ).click()

            # Attendre un certain temps pour que le téléchargement se termine
            time.sleep(3)
            
            
            if numero_page > 1:
                # Attente pour l'iFrame contenant le reCAPTCHA et basculer vers celui-ci, comme avec une nouvelle fenêtre
                # Cependant, les iFrame ont une structure particulière et je ne suis arrivé à l'indentifier
                # grâce à son XPath, qui commence par un nom (@name) commençant par 'a-' et 
                # une source (@src) commençant par 'https://www.google.com/recaptcha'
                wait = WebDriverWait(driver, 15)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@name,'a-') and starts-with (@src, 'https://www.google.com/recaptcha')]")))
                
                # Attente pour que le bouton reCAPTCHA devienne cliquable et clicker dessus
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='recaptcha-checkbox-border']"))).click()
            
                # Revenir au contenu principal de la page car après avoir clicker, une mini fenêtre apparait
                driver.switch_to.default_content()
            
                # Un court délai pour permettre à la page de traiter l'action du reCAPTCHA
                time.sleep(2)
            
                # Utiliser JavaScript pour cliquer sur le bouton "Vérifier" car l'élément est caché ou superposé
                # JavaScript permet de "forcer" le click sur un bouton bien qu'il soit caché ou superposé
                verify_button = wait.until(EC.presence_of_element_located((By.ID, "verifyUser")))
                driver.execute_script("arguments[0].click();", verify_button)
                 
                time.sleep(2)
                
                # Utiliser JavaScript pour déclencher l'événement onclick du bouton "Continuer"
                driver.execute_script("ConfirmRecaptchaClick();")
            
            # Après le téléchargement de chaque fichier, nous souhaitons renommer le fichier sous le format 
            # {nom_commune}_{type_catastrophe}_{date_debut_formattee}_p{numero_page}
            # Pour cela, on récupère à chaque ligne, les informations nécessaire et on les stockent dans nouveau_nom
            chemin_fichier_telecharge = obtenir_dernier_fichier(dossier_telechargements)
            if chemin_fichier_telecharge:
                nom_commune = row['lib_commune'].replace('/', ' ')
                premier_mot_risque = row['lib_risque_jo'].replace('/', ' ').split()[0]
                date_debut_formattee = date_debut.strftime('%Y%m%d')
                nouveau_nom = f"{nom_commune}_{premier_mot_risque}_{date_debut_formattee}_p{numero_page}.rtf"
                os.rename(chemin_fichier_telecharge, os.path.join(dossier_telechargements, nouveau_nom))
        
               

            # Désélectionner tous les articles (cela est nécessaire pour ne pas télécharger deux fois la même chose)
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"][onclick^="selectAll"]'))
            ).click()
            
            
            # Passer à la page suivante si elle existe.
            try:
                next_page_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.nextItem'))
                )
                next_page_btn.click()
                WebDriverWait(driver, 30).until(EC.staleness_of(next_page_btn))
                numero_page += 1
            except TimeoutException:
                derniere_page = True
                
        # Retour à la page de recherche initiale dans le cas où aucune page suivante n'est trouvée
        driver.get("https://global-factiva-com.scd-rproxy.u-strasbg.fr/sb/default.aspx?lnep=hp")  # Remplacez par l'URL réelle
        
        time.sleep(5)

    except Exception as e:
        print(f"Erreur lors du traitement de la ligne {index}: {e}")


# Fermeture du navigateur après le traitement de toutes les lignes
driver.quit()

