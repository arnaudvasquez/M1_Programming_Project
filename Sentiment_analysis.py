#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:07:52 2024

@author: mateo
"""

import pandas as pd
from transformers import pipeline
from striprtf.striprtf import rtf_to_text
import os

# Chemin vers le fichier CSV
chemin_fichier_csv = '/Users/mateo/~/Desktop/Fac Strasbourg/Mémoire/Donnees_GASPAR/catnat_gaspar.csv'
df = pd.read_csv(chemin_fichier_csv, sep=';')

# Initialisation de la pipeline pour l'analyse de sentiments avec CamemBERT
analyseur_de_sentiments = pipeline("sentiment-analysis", model="camembert-base")

# Création d'un nouveau DataFrame pour stocker les résultats
df_resultats = pd.DataFrame()

# Fonction pour lire et convertir le contenu RTF en texte brut
def lire_texte_rtf(chemin_fichier):
    with open(chemin_fichier, 'r') as fichier:
        contenu_rtf = fichier.read()
    return rtf_to_text(contenu_rtf)

# Fonction pour trouver les paragraphes contenant un mot-clé spécifique
def trouver_paragraphes_contenant_mot_cle(texte, mot_cle):
    paragraphes = texte.split('\n')
    return [para for para in paragraphes if mot_cle.lower() in para.lower()]

# Fonction pour l'analyse de sentiments avec CamemBERT
def analyser_sentiments_camembert(paragraphe):
    resultats = analyseur_de_sentiments(paragraphe)
    if resultats:
        # Retourner le premier résultat de l'analyse
        return resultats[0]  # Ceci est un dictionnaire avec les clés 'label' et 'score'
    else:
        return {"label": "NEUTRAL", "score": 0}  # Retourner une valeur par défaut si aucun résultat


# Parcours du DataFrame pour traiter chaque fichier
for index, row in df.iterrows():
    nom_commune = row['lib_commune']
    type_catastrophe = row['lib_risque_jo'].split()[0]
    date_catastrophe = pd.to_datetime(row['dat_deb']).strftime('%Y%m%d')
    chemin_fichier_rtf = f'/Users/mateo/downloads/{nom_commune}_{type_catastrophe}_{date_catastrophe}_p1.rtf'

    # Vérification de l'existence du fichier
    if not os.path.exists(chemin_fichier_rtf):
        print(f"Fichier non trouvé : {chemin_fichier_rtf}")
        continue

    # Lecture et conversion du fichier RTF
    texte_brut = lire_texte_rtf(chemin_fichier_rtf)
    if texte_brut is None:
        continue

    # Recherche de paragraphes contenant le type de catastrophe
    paragraphes_pertinents = trouver_paragraphes_contenant_mot_cle(texte_brut, type_catastrophe)

    # Stockage des résultats
    resultat_paragraphe = []
    for paragraphe in paragraphes_pertinents:
        resultat = analyser_sentiments_camembert(paragraphe)  # C'est un dictionnaire
        score_sentiment = resultat['score']  # Obtenir le score
        label_sentiment = resultat['label']  # Obtenir l'étiquette
        # Stocker le résultat
        resultat_paragraphe.append((paragraphe, label_sentiment, score_sentiment))

    # Création d'un DataFrame temporaire pour la nouvelle ligne
    nouvelle_ligne = pd.DataFrame([row])
    for i, (texte, label, score) in enumerate(resultat_paragraphe):
        nouvelle_ligne[f'Texte_Paragraphe_{i+1}'] = [texte]
        nouvelle_ligne[f'Label_Sentiment_{i+1}'] = [label]
        nouvelle_ligne[f'Score_Sentiment_{i+1}'] = [score]

    # Concaténer avec le DataFrame principal
    df_resultats = pd.concat([df_resultats, nouvelle_ligne], ignore_index=True)


# Affichage du DataFrame contenant les résultats
print(df_resultats.head())
