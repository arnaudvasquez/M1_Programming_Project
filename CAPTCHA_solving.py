#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 00:18:46 2024

@author: mateo
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

# Chemin vers le webdriver
driver = webdriver.Firefox()

# Accéder à la page de la BU Unistra
driver.get("https://bu.unistra.fr/opac/resource/factiva/BUS1884906?tabDoc=tabcontiene")


# Attendre que la nouvelle fenêtre soit ouverte
time.sleep(2)  # Ajuster ce temps selon la vitesse de chargement de la page


# Attendre et cliquer sur le lien pour accéder à Factiva
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[target='new']"))
).click()

# Attendre que la nouvelle fenêtre soit ouverte
time.sleep(2)  


# Basculer vers la nouvelle fenêtre
window_after = driver.window_handles[1]
driver.switch_to.window(window_after)


# Attendre et entrer le nom d'utilisateur
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "username"))
).send_keys("username")

# Attendre et entrer le mot de passe
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "password"))
).send_keys("password")

# Attendre et cliquer sur le bouton de connexion
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.ID, "login-btn"))
).click()


time.sleep(15)

# Basculer vers la nouvelle fenêtre
window_after = driver.window_handles[1]
driver.switch_to.window(window_after)

time.sleep(15)

# Sélectionner la région "Europe"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Région')]"))
).click()

# Attendre et cliquer sur le bouton "+" pour "Europe"
plus_button_xpath = "//a[contains(text(), 'Europe')]/preceding-sibling::span[@class='mnuBtn']/span"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, plus_button_xpath))
).click()



# Étendre la section "Europe de l'Ouest"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ouest')]/preceding::span[@class='mnuBtn'][1]"))
).click()



# Cliquer sur "France"
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'France')]"))
).click()

# Attendre un peu pour s'assurer que la section s'est bien étendue
time.sleep(5)






# Liste des mots clés ou expressions à rechercher
mot_cle= [
    "Inondation"
]


# Localiser le champ de recherche
champ_recherche = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".ace_text-input"))
)


# Effacer le champ de recherche avant d'entrer un nouveau mot clé
champ_recherche.clear()

# Entrer le mot clé dans le champ de recherche
champ_recherche.send_keys(mot_cle)


# Simuler l'envoi de la requête
champ_recherche.send_keys(Keys.RETURN)

# Attendre un certain temps pour que le téléchargement se termine
time.sleep(10)

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
    time.sleep(5)
    
    if numero_page > 1:
        # Attente pour l'iFrame contenant le reCAPTCHA et basculement vers celui-ci
        wait = WebDriverWait(driver, 15)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@name,'a-') and starts-with (@src, 'https://www.google.com/recaptcha')]")))
        
        # Attente pour que le bouton reCAPTCHA devienne cliquable et clic sur celui-ci
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='recaptcha-checkbox-border']"))).click()
    
        # Revenir au contenu principal de la page
        driver.switch_to.default_content()
    
        # Un court délai pour permettre à la page de traiter l'action du reCAPTCHA
        time.sleep(2)
    
        # Utiliser JavaScript pour cliquer sur le bouton "Vérifier"
        verify_button = wait.until(EC.presence_of_element_located((By.ID, "verifyUser")))
        driver.execute_script("arguments[0].click();", verify_button)
         
        time.sleep(5)
    
        # Utiliser JavaScript pour déclencher l'événement onclick du bouton "Continuer"
        driver.execute_script("ConfirmRecaptchaClick();")
   
    time.sleep(5)
                                
    # Désélectionner tous les articles
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"][onclick^="selectAll"]'))
    ).click()

    try:
        next_page_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.nextItem'))
        )
        next_page_btn.click()
        WebDriverWait(driver, 30).until(EC.staleness_of(next_page_btn))
        numero_page += 1
    except TimeoutException:
        derniere_page = True

# Fermer le navigateur
driver.quit()




