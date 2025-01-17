import os
import csv
from datetime import datetime

def save_feedback(rating, chat_history):
    """
    Sauvegarde les évaluations utilisateur dans un fichier CSV avec des détails sur la conversation et 
    l'emplacement de l'utilisateur.

    Args:
        rating (int): La note donnée par l'utilisateur. Doit être un entier (par exemple, sur une échelle de 1 à 5).
        chat_history (str): L'historique de la conversation entre l'utilisateur et le système.
    """
    # Obtient la date et l'heure actuelles dans un format lisible.
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Appelle la fonction pour récupérer les informations d'emplacement de l'utilisateur.
    ip, city, region, country = get_location_info()

    # Structure les données à écrire dans le fichier CSV.
    data_to_write = [current_datetime, chat_history, rating, ip, city, region, country]

    # Ouvre (ou crée si nécessaire) le fichier CSV en mode ajout.
    with open("feedback.csv", mode="a", newline='', encoding="utf-8") as file:
        # Vérifie si le fichier est vide (pour écrire l'en-tête si nécessaire).
        file_empty = os.stat("feedback.csv").st_size == 0
        writer = csv.writer(file, delimiter=";")

        # Écrit l'en-tête des colonnes si le fichier est vide.
        if file_empty:
            writer.writerow(["Date", "Historique de la conversation", "Note", "IP", "Ville", "Region", "Pays"])

        # Écrit les données de feedback dans une nouvelle ligne du fichier CSV.
        writer.writerow(data_to_write)

def get_location_info():
    """
    Récupère les informations d'emplacement de l'utilisateur en utilisant l'API IPinfo.

    Returns:
        tuple: Contient l'adresse IP, la ville, la région et le pays de l'utilisateur.
            - "ip" : L'adresse IP de l'utilisateur.
            - "city" : La ville correspondant à l'IP.
            - "region" : La région correspondant à l'IP.
            - "country" : Le code ISO du pays correspondant à l'IP.
            - En cas d'erreur ou d'absence d'information, retourne "Inconnue" pour chaque champ.
    """
    import requests  # Import nécessaire pour envoyer des requêtes HTTP.

    # Jeton d'accès pour l'API IPinfo (remplacer par un token valide si nécessaire).
    ipinfo_token = "ec7847dfb8277c"
    url = f"https://ipinfo.io?token={ipinfo_token}"

    # Envoie une requête GET à l'API IPinfo.
    response = requests.get(url)

    # Si la requête est réussie, traite les données de localisation reçues.
    if response.status_code == 200:
        location_data = response.json()
        return (
            location_data.get("ip", "Inconnue"),       # Adresse IP de l'utilisateur.
            location_data.get("city", "Inconnue"),     # Ville.
            location_data.get("region", "Inconnue"),   # Région.
            location_data.get("country", "Inconnu")    # Code pays.
        )

    # En cas d'erreur (requête échouée), retourne des valeurs par défaut.
    return "Inconnue", "Inconnue", "Inconnue", "Inconnu"
