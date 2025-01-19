import calendar
import pandas as pd
import streamlit as st

def apply_filters(df : pd.DataFrame) -> pd.DataFrame:
    """
    Applique les filtres de pays, mois et année sur les données.

    Args:
        df (DataFrame): Données principales.

    Returns:
        DataFrame: Données filtrées.
    """
    st.sidebar.header("Filtres")

    # Filtre de pays
    liste_pays = ["Tout"] + list(df['Pays'].unique())
    pays_selectionnes = st.sidebar.multiselect("Filtrer par pays :", options=liste_pays, default="Tout")
    pays_filtre = df['Pays'].unique() if "Tout" in pays_selectionnes else pays_selectionnes

    # Filtre de mois
    mois_options = ["Tout"] + [calendar.month_name[i] for i in range(1, 13)]
    mois_selectionne = st.sidebar.selectbox("Mois :", options=mois_options)
    mois_filtre = None if mois_selectionne == "Tout" else mois_options.index(mois_selectionne)

    # Filtre d'année
    annees_options = ["Tout"] + sorted(df['Date'].dt.year.unique())
    annee_selectionnee = st.sidebar.selectbox("Année :", options=annees_options)
    annee_filtre = None if annee_selectionnee == "Tout" else int(annee_selectionnee)

    # Application des filtres
    df_filtre = df[
        (df['Pays'].isin(pays_filtre)) &
        ((df['Date'].dt.month == mois_filtre) if mois_filtre else True) &
        ((df['Date'].dt.year == annee_filtre) if annee_filtre else True)
    ]
    print(df_filtre)
    return df_filtre
