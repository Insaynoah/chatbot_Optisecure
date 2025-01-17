import folium
import pandas as pd
from branca.colormap import linear
from folium.plugins import MarkerCluster

def create_map(data : pd.DataFrame, country_coordinates) -> folium.Map:
    """
    Crée une carte interactive avec Folium en fonction des notes moyennes par pays.

    Args:
        data (pd.DataFrame): Données contenant les informations sur les pays, notes moyennes, etc.
            - Doit inclure au minimum les colonnes :
                - 'Alpha-2 code' : Code ISO alpha-2 du pays.
                - 'Note moyenne' : Moyenne des notes pour le pays.
                - 'Nombre' : Nombre total de notes attribuées au pays.
                - 'URL' : Lien vers un drapeau ou une image associée au pays.
                - 'Country' : Nom du pays.
        country_coordinates (GeoDataFrame): Données géographiques des pays, incluant les géométries et les codes ISO alpha-2.

    Returns:
        folium.Map: Objet Folium représentant la carte interactive.
    """

    # Création de la carte centrée sur l'Europe, avec un niveau de zoom de départ.
    m = folium.Map(location=[54.5260, 15.2551], zoom_start=4)

    # Création d'une échelle de couleur (colormap) basée sur les notes moyennes.
    colormap = linear.RdYlGn_09.scale(data['Note moyenne'].min(), data['Note moyenne'].max())
    colormap.add_to(m)  # Ajout de la colormap à la carte.

    # Ajout d'un regroupement de marqueurs pour améliorer la lisibilité.
    marker_cluster = MarkerCluster().add_to(m)

    # Fonction pour styliser les polygones des pays selon la note moyenne.
    def style_function(note):
        return {
            'fillColor': colormap(note),  # Couleur remplie selon la note.
            'color': 'black',            # Couleur du contour (noir).
            'weight': 1,                 # Épaisseur du contour.
            'fillOpacity': 0.5           # Opacité de la couleur remplie.
        }

    # Boucle sur chaque ligne des données pour ajouter les géométries et les infobulles.
    for _, row in data.iterrows():
        pays = row['Alpha-2 code']  # Code ISO alpha-2 du pays.
        note = round(row['Note moyenne'], 2)  # Note moyenne arrondie à 2 décimales.
        count = row["Nombre"]  # Nombre total de notes.
        flag_url = row["URL"]  # URL du drapeau ou image associée.
        country_name = row["Country"]  # Nom du pays.

        # Filtrage pour obtenir les données géographiques du pays actuel.
        country_data = country_coordinates[country_coordinates['ISO_A2_EH'] == pays]

        # Si des données géographiques existent pour ce pays :
        if not country_data.empty:
            geometry = country_data.geometry.iloc[0]  # Extraction de la géométrie.

            # Conversion en liste si la géométrie est un polygone ou un multipolygone.
            if geometry.geom_type == 'Polygon':
                geometry = [geometry]
            elif geometry.geom_type == 'MultiPolygon':
                geometry = list(geometry.geoms)

            # Ajout de chaque polygone avec le style et un tooltip.
            for polygon in geometry:
                tooltip = f"""
                <img src='{flag_url}' width='20' style='vertical-align:middle;'/>
                <strong>{country_name}</strong><br>
                Note moyenne : <strong>{note}</strong><br>
                Nombre de notes : <strong>{count}</strong>
                """
                folium.GeoJson(
                    polygon,
                    style_function=lambda x, note=note: style_function(note),  # Style dynamique basé sur la note.
                    tooltip=tooltip  # Infobulle contenant les informations du pays.
                ).add_to(m)

    # Retourne l'objet Folium Map.
    return m
