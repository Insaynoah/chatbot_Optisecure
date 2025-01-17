import streamlit as st
import pandas as pd
from modules.auth import authenticate_user
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.kpi import display_kpi
from modules.map_creator import create_map
from modules.utils import create_star_rating
from modules.wordcloud_utils import afficher_nuage_de_mots
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(
    page_title="Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style de la barre latérale
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        width: 200px;
        min-width: 200px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Chargement des données
df, country_coordinates, flags = load_data()

# Authentification
if not authenticate_user():
    st.stop()

# Filtres
df_filtre = apply_filters(df)

# Affichage des KPI et de la carte
if df_filtre.empty:
    st.warning("⚠️ Aucun pays ou aucune donnée disponible pour cette sélection.")
else:
    moyenne = df_filtre['Note'].mean()
    st.title("📊 Dashboard de satisfaction")
    st.subheader("Indicateurs clés")
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        display_kpi("⭐", f"Note moyenne ({create_star_rating(moyenne)})", round(moyenne, 2) if not pd.isnull(moyenne) else "N/A", "#f0f4ff")
    with kpi2:
        display_kpi("📋", "Nombre de feedbacks", len(df_filtre), "#fdf6ec")

    # Carte et tableau
    city_avg_note_filtre = df_filtre.groupby('Pays').agg(
        Moyenne_Note=('Note', 'mean'),
        Nombre=('Note', 'count')
    ).reset_index().rename(columns={"Moyenne_Note": "Note moyenne"})
    city_avg_note_filtre = city_avg_note_filtre.merge(flags, left_on='Pays', right_on='Alpha-2 code', how='left')

    tab1, tab2 = st.tabs(["📊 Indicateurs + Carte", "📜 Nuage de mots"])
    with tab1:
        table_col, map_col = st.columns([3, 7], gap="large")
        with table_col:
            st.subheader("📋 Notes par pays")
            st.write(city_avg_note_filtre[['Pays', 'Note moyenne', 'Nombre']].to_html(escape=False, index=False), unsafe_allow_html=True)
        with map_col:
            st.subheader("🗺️ Carte interactive des notes")
            map_object = create_map(city_avg_note_filtre, country_coordinates)
            st_folium(map_object, height=600, width=900)

    with tab2:
        st.title("📜 Nuage de mots")
        afficher_nuage_de_mots(df_filtre['Historique de la conversation'], titre="Historique des conversations")
