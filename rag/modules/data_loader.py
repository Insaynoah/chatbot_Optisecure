import pandas as pd
import geopandas as gpd
import streamlit as st

@st.cache_data
def load_data() -> tuple:
    """
    Charge les données nécessaires à l'application, avec une mise en cache pour optimiser les performances.

    Decorator:
        @st.cache_data : Cache les résultats de la fonction pour éviter de recharger les données
        à chaque exécution si les entrées n'ont pas changé.

    Returns:
        tuple: Un tuple contenant trois éléments :
            - df (DataFrame) : Données principales provenant du fichier `feedback.csv`.
                - Colonnes attendues : 
                    - "Date" : Date et heure de l'enregistrement (convertie en type datetime).
                    - D'autres colonnes basées sur le format du fichier CSV (par exemple, notes, IP, etc.).
            - country_coordinates (GeoDataFrame) : Données géographiques des pays.
                - Chargées depuis un fichier shapefile.
                - CRS (système de coordonnées) converti en EPSG:4326 (utilisé pour les cartes interactives).
            - flags (DataFrame) : Données des drapeaux, associées aux codes ISO des pays.
                - Colonnes attendues : "ISO" (code ISO des pays), "URL" (liens des drapeaux), etc.
    """

    # Charge le fichier CSV contenant les retours d'utilisateur dans un DataFrame.
    df = pd.read_csv('feedback.csv', delimiter=";")

    # Charge les données géographiques des pays depuis un shapefile.
    country_coordinates = gpd.read_file("data/ne_110m_admin_0_countries.shp")

    # Charge les données des drapeaux des pays depuis un fichier CSV.
    flags = pd.read_csv("data/flags_iso.csv", delimiter=",")

    # Convertit le système de coordonnées des données géographiques en EPSG:4326 (longitude/latitude).
    country_coordinates = country_coordinates.to_crs(epsg=4326)

    # Convertit la colonne "Date" en type datetime pour faciliter les analyses temporelles.
    df['Date'] = pd.to_datetime(df['Date'])

    # Retourne les trois objets : données principales, géométries des pays et données des drapeaux.
    return df, country_coordinates, flags

