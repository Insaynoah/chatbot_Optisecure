
import streamlit as st

def display_kpi(icon: str, label: str, value: float, color: str) -> None:
    """
    Affiche un KPI stylisé.

    Args:
        icon (str): Icône pour le KPI (ex. : "⭐", "📋").
        label (str): Libellé pour décrire le KPI.
        value (float): Valeur du KPI.
        color (str): Couleur d'arrière-plan du KPI (ex. : "#f0f4ff").
    """
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
