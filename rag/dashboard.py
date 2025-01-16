import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Chatbot Feedback Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Chargement des données du fichier feedback.csv
df = pd.read_csv('feedback.csv',delimiter=";")

# Convertir la colonne "Date" en datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculer la note moyenne
average_note = df['Note'].mean()

# Créer un graphique avec Plotly pour afficher la note moyenne avec des étoiles
def create_star_rating(note):
    stars = '★' * int(note) + '☆' * (5 - int(note))
    return stars

# Dashboard
st.title("Dashboard de Satisfaction des Conversations")

# Indicateur clé - Note de satisfaction moyenne avec étoiles
st.header("Indicateur clé 1 : Note moyenne de satisfaction")
st.write(f"Note moyenne : {average_note:.2f} / 5")
st.markdown(f"Évaluation : {create_star_rating(average_note)}", unsafe_allow_html=True)

# Indicateur clé - Nombre de requêtes
st.header("Indicateur clé 2 : Nombre total de requêtes")
st.write(f"Nombre de requêtes : {len(df)}")

# Carte - Affichage des villes et de leurs notes moyennes
st.header("Carte des Notes de Satisfaction par Ville")

# Calculer la note moyenne par ville
city_avg_note = df.groupby('Ville')['Note'].mean().reset_index()

# Créer une carte interactive avec Plotly
fig = px.scatter_geo(city_avg_note, locations="Ville", size="Note", hover_name="Ville",
                     color="Note", color_continuous_scale="Viridis", projection="natural earth",
                     title="Notes de Satisfaction par Ville")

# Afficher la carte
st.plotly_chart(fig)