import calendar
import streamlit as st
import pandas as pd
import geopandas as gpd
from branca.colormap import linear
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style pour réduire la taille de la barre latérale
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
@st.cache_data
def load_data():
    df = pd.read_csv('feedback.csv', delimiter=";")
    country_coordinates = gpd.read_file("data/ne_110m_admin_0_countries.shp")
    flags = pd.read_csv("data/flags_iso.csv", delimiter=",")
    country_coordinates = country_coordinates.to_crs(epsg=4326)
    df['Date'] = pd.to_datetime(df['Date'])
    return df, country_coordinates, flags

df, country_coordinates, flags = load_data()

# Calculs des statistiques principales
city_avg_note = df.groupby('Pays').agg(
    Moyenne_Note=('Note', 'mean'),
    Nombre=('Note', 'count')
).reset_index().rename(columns={"Moyenne_Note": "Note moyenne"})
city_avg_note = city_avg_note.merge(flags, left_on='Pays', right_on='Alpha-2 code', how='left')

# Fonction pour créer les étoiles
def create_star_rating(note):
    if pd.isnull(note):
        return "Aucune donnée"
    note = round(note * 2) / 2
    full_stars = '🌕' * int(note)
    half_star = '🌗' if note % 1 != 0 else ''
    empty_stars = '🌑' * (5 - len(full_stars) - (1 if half_star else 0))
    return full_stars + half_star + empty_stars

# Fonction pour créer une carte Folium
def create_map(data, country_coordinates):
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=2)
    colormap = linear.RdYlGn_09.scale(df['Note'].min(), df['Note'].max())
    colormap.add_to(m)
    marker_cluster = MarkerCluster().add_to(m)

    def style_function(note):
        return {
            'fillColor': colormap(note),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5
        }

    for _, row in data.iterrows():
        pays = row['Alpha-2 code']
        note = round(row['Note moyenne'], 2)
        count = row["Nombre"]
        flag_url = row["URL"]
        country_name = row["Country"]
        country_data = country_coordinates[country_coordinates['ISO_A2_EH'] == pays]

        if not country_data.empty:
            geometry = country_data.geometry.iloc[0]
            if geometry.geom_type == 'Polygon':
                geometry = [geometry]
            elif geometry.geom_type == 'MultiPolygon':
                geometry = list(geometry.geoms)
            for polygon in geometry:
                tooltip = f"<img src='{flag_url}' width='20' style='vertical-align:middle;'/> <strong>{country_name}</strong><br>{create_star_rating(note)}<br>Note moyenne : <strong>{note}</strong><br>Nombre de notes : <strong>{count}</strong>"
                folium.GeoJson(polygon, style_function=lambda x, note=note: style_function(note), tooltip=tooltip).add_to(m)

    return m

# Fonction pour afficher des KPI stylisés
def display_kpi(icon, label, value, color):
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; background-color: {color}; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <div style="font-size: 30px; margin-right: 15px;">{icon}</div>
            <div>
                <div style="font-size: 16px; font-weight: bold;">{label}</div>
                <div style="font-size: 24px; font-weight: bold;">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Création des filtres
st.sidebar.header("Filtres")

# Filtre de pays avec option "Tout"
liste_pays = df['Pays'].unique()
liste_pays = ["Tout"] + list(liste_pays)  # Ajoute "Tout" comme première option
pays_selectionnes = st.sidebar.multiselect(
    "Filtrer par pays :", 
    options=liste_pays, 
    default="Tout"  # Par défaut, "Tout" est sélectionné
)


# Filtre temporel (mois et année)
# Liste des mois avec "Tout" comme option
mois_options = ["Tout"] + [calendar.month_name[i] for i in range(1, 13)]
mois_selectionne = st.sidebar.selectbox("Mois :", options=mois_options)

# Convertir le mois sélectionné en son numéro, ou ne pas filtrer si "Tout" est sélectionné
if mois_selectionne == "Tout":
    mois_filtre = None  # Pas de filtrage par mois
else:
    mois_filtre = mois_options.index(mois_selectionne)  # Numéro du mois sélectionné

# Liste des années avec "Tout" comme option
annees_options = ["Tout"] + sorted(df['Date'].dt.year.unique())
annee_selectionnee = st.sidebar.selectbox("Année :", options=annees_options)

# Convertir l'année sélectionnée en un filtre, ou ne pas filtrer si "Tout" est sélectionné
if annee_selectionnee == "Tout":
    annee_filtre = None  # Pas de filtrage par année
else:
    annee_filtre = int(annee_selectionnee)  # Année sélectionnée

# Gérer la sélection de "Tout"
if "Tout" in pays_selectionnes:
    pays_filtre = df['Pays'].unique()  # Inclut tous les pays
else:
    pays_filtre = pays_selectionnes  # Filtrer uniquement les pays sélectionnés

# Application des filtres aux données
df_filtre = df[
    (df['Pays'].isin(pays_filtre)) &  # Filtrer par pays
    ((df['Date'].dt.month == mois_filtre) if mois_filtre else True) &  # Filtrer par mois
    ((df['Date'].dt.year == annee_filtre) if annee_filtre else True)  # Filtrer par année
]

# Vérification : y a-t-il des données après le filtrage ?
if df_filtre.empty:
    st.warning("⚠️ Aucun pays ou aucune donnée disponible pour cette sélection.")
else:
    city_avg_note_filtre = df_filtre.groupby('Pays').agg(
        Moyenne_Note=('Note', 'mean'),
        Nombre=('Note', 'count')
    ).reset_index().rename(columns={"Moyenne_Note": "Note moyenne"})
    city_avg_note_filtre = city_avg_note_filtre.merge(flags, left_on='Pays', right_on='Alpha-2 code', how='left')

    # Création des onglets
    tab1, tab2 = st.tabs(["📊 Indicateurs + Carte", "📜 Nuage de mots"])

    # Contenu du premier onglet
    with tab1:
        st.title("📊 Dashboard de satisfaction")
        st.subheader("Indicateurs clés")

        # Section des KPI
        kpi1, kpi2 = st.columns(2)
        with kpi1:
            moyenne = df_filtre['Note'].mean()
            display_kpi(
                icon="⭐",
                label=f"Note moyenne ({create_star_rating(moyenne)})",
                value=round(moyenne, 2) if not pd.isnull(moyenne) else "N/A",
                color="#f0f4ff"
            )
        with kpi2:
            display_kpi(
                icon="📋",
                label="Nombre de feedbacks",
                value=len(df_filtre),
                color="#fdf6ec"
            )

        # Section tableau et carte en deux colonnes
        table_col, map_col = st.columns([3, 7], gap="large")

        with table_col:
            st.subheader("📋 Notes par pays")
            city_avg_note_filtre['Pays'] = city_avg_note_filtre.apply(
                lambda x: f'<img src="{x["URL"]}" width="20"/> {x["Country"]}' if pd.notnull(x["URL"]) else x["Country"],
                axis=1
            )
            st.write(city_avg_note_filtre[['Pays', 'Note moyenne', 'Nombre']].round(2).to_html(escape=False, index=False), unsafe_allow_html=True)

        with map_col:
            st.subheader("🗺️ Carte interactive des notes")
            map_object = create_map(city_avg_note_filtre, country_coordinates)
            st_folium(map_object, height=600, width=900)

    # Contenu du deuxième onglet
    with tab2:
        st.title("📜 Nuage de mots")

        # Fonction pour afficher un nuage de mots
        def afficher_nuage_de_mots(colonne, titre="Nuage de Mots", max_mots=200):
            text = " ".join(colonne.dropna().astype(str).tolist())
            wordcloud = WordCloud(background_color='white', colormap='viridis', max_words=max_mots).generate(text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.subheader(titre)
            st.pyplot(fig)

        afficher_nuage_de_mots(df_filtre['Historique de la conversation'], titre="Historique des conversations")
