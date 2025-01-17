import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def afficher_nuage_de_mots(colonne: pd.Series, titre="Nuage de Mots", max_mots=200) -> None:
    """
    Génère et affiche un nuage de mots à partir d'une colonne de texte.

    Args:
        colonne (pd.Series): Colonne contenant les données textuelles à analyser.
        titre (str): Titre affiché au-dessus du nuage de mots. Par défaut, "Nuage de Mots".
        max_mots (int): Nombre maximum de mots à inclure dans le nuage de mots. Par défaut, 200.

    La fonction :
        - Vérifie si la colonne de texte est non vide et contient des données valides.
        - Convertit toutes les valeurs de la colonne en texte et les fusionne pour créer un seul corpus.
        - Génère un nuage de mots en utilisant la bibliothèque WordCloud.
        - Affiche le nuage de mots à l'aide de Matplotlib et Streamlit.
        - Si la colonne est vide ou invalide, un message d'avertissement est affiché.
    """
    
    # Vérifie si la colonne est non vide et contient des données
    if colonne is not None and not colonne.empty:
        # Combine toutes les valeurs textuelles de la colonne en une seule chaîne
        text = " ".join(colonne.dropna().astype(str).tolist())

        # Crée un nuage de mots avec les paramètres spécifiés
        wordcloud = WordCloud(
            background_color='white',  # Fond de l'image du nuage de mots
            colormap='viridis',        # Palette de couleurs utilisée dans le nuage de mots
            max_words=max_mots         # Nombre maximum de mots à afficher
        ).generate(text)

        # Crée une figure et un axe pour afficher le nuage de mots
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')  # Affiche l'image du nuage de mots
        ax.axis('off')  # Désactive les axes autour du nuage de mots
        st.subheader(titre)  # Affiche un titre au-dessus du nuage de mots
        st.pyplot(fig)  # Affiche le nuage de mots via Streamlit

    else:
        # Si la colonne est vide ou invalide, affiche un message d'avertissement
        st.warning("⚠️ Aucune donnée textuelle disponible pour générer un nuage de mots.")
