import streamlit as st
import requests
import json
import csv
from datetime import datetime
import os
from bdd import *

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Votre clé API Gemini
api_key = "AIzaSyB5TvLH3-6CqNL09eEAEvGO9frgt5UNwk4"  # Remplacez par votre véritable clé API
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

if "rating" not in st.session_state:
        st.session_state['rating'] = 0  # Initialiser le rating si ce n'est pas déjà fait


st.logo(icon_image='https://i.ibb.co/MSZB1qp/Marceline-1.png', image='https://i.ibb.co/MSZB1qp/Marceline-1.png', size='large')

# Définir le titre de l'application
st.title("Chatbot OptiSecure Assurances")

# Ajouter le système d'avis dans la sidebar
with st.sidebar:
    st.subheader("Évaluez la réponse de l'assistant (0 à 5)")
    
    # Slider pour évaluation
    rating = st.slider("Sélectionnez une note", min_value=0, max_value=5, step=1, key="rating")
    
    # Ajouter un bouton Soumettre
    if st.button("Soumettre l'évaluation"):
        # Obtenez la date et l'heure actuelles
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history = " ".join([msg["content"] for msg in st.session_state.messages])  # Historique des messages
        
        ipinfo_token = "ec7847dfb8277c" 

        # Effectuer la requête à l'API avec le token
        url = f"https://ipinfo.io?token={ipinfo_token}"
        response = requests.get(url)

        if response.status_code == 200:
            # Extraire les données de localisation
            location_data = response.json()
            city = location_data.get("city", "Inconnue")
            region = location_data.get("region", "Inconnue")
            country = location_data.get("country", "Inconnu")
            ip = location_data.get("ip", "Inconnue")
            
        data_to_write = [current_datetime, chat_history, rating, ip, city, region, country]
                
        
        # Écrire dans le fichier CSV
        with open("feedback.csv", mode="a", newline='', encoding="utf-8") as file:
            file_empty = os.stat("feedback.csv").st_size == 0
            writer = csv.writer(file,delimiter=";")
            
            if file_empty:  # Ajouter l'entête si le fichier est vide
                writer.writerow(["Date", "Historique de la conversation", "Note", "IP", "Ville", "Region", "Pays"])
            writer.writerow(data_to_write)
        
        st.write(f"Merci pour votre évaluation : {rating}")
                
# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []  # Si aucun historique n'existe, on initialise une liste vide

# Accepter l'entrée de l'utilisateur
prompt = st.chat_input("Que voulez-vous savoir sur les contrats d'OptiSecure Assurances ?")  # Demander à l'utilisateur de saisir un message



# Afficher les messages de l'historique de la conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # Rôle du message ('user' ou 'assistant')
        st.markdown(message["content"])  # Afficher le contenu du message


# Lorsque l'utilisateur soumet un message
if prompt:
    # Ajouter le message de l'utilisateur à l'historique de la conversation
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Afficher le message de l'utilisateur dans la fenêtre de chat
    with st.chat_message("user"):
        st.markdown(prompt)

    reponses_chroma = requete_chromadb(prompt)
    reponses_chroma = dict(zip(reponses_chroma['distances'][0], reponses_chroma['documents'][0]))
    min_distance = min(reponses_chroma.keys())

    # Identifier les distances proches dans un seuil par rapport à la distance minimale
    threshold = 0.05  # Ajuster le seuil selon les besoins
    close_distances = [dist for dist in reponses_chroma.keys() if abs(dist - min_distance) <= threshold]

    # Préparer la réponse en fonction des distances
    if len(st.session_state.messages) == 1:
        if min_distance > 0.8:
            prompt_entier = (
                "Tu dois agir durant toute la conversation comme un agent pour une assurance : Optisecure. "
                "Si la question suivante n'a aucun sens ou est en rapport avec les assurances mais n'est pas assez détaillée, "
                "demande plus de détails/informations. Question : " + prompt
            )
        elif len(close_distances) > 1:
            # Plusieurs réponses proches trouvées
            options = "\n".join([f"Option {i + 1}: {reponses_chroma[dist]}" for i, dist in enumerate(close_distances)])
            prompt_entier = (
                "Tu dois agir durant toute la conversation comme un agent pour une assurance : Optisecure. "
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici plusieurs réponses possibles qui sont très proches :\n" + options + 
                "\nExplique pourquoi une réponse claire ne peut être donnée et propose une reformulation basée sur ces options."
            )
        else:
            meilleur_reponse = reponses_chroma[min_distance]
            prompt_entier = (
                "Tu dois agir durant toute la conversation comme un agent pour une assurance : Optisecure. "
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici la réponse que tu dois reformuler : " + meilleur_reponse
            )
    else:
        if min_distance > 0.8:
            prompt_entier = (
                "Si la question suivante n'est pas en rapport avec les assurances, demande de poser une question par rapport aux assurances. "
                "Sinon, demande plus de détails et ne réponds pas à la question posée. Question : " + prompt
            )
        elif len(close_distances) > 1:
            # Plusieurs réponses proches trouvées
            options = "\n".join([f"Option {i + 1}: {reponses_chroma[dist]}" for i, dist in enumerate(close_distances)])
            prompt_entier = (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici plusieurs réponses possibles qui sont très proches :\n" + options + 
                "\nExplique pourquoi une réponse claire ne peut être donnée et propose une reformulation basée sur ces options."
            )
        else:
            meilleur_reponse = reponses_chroma[min_distance]
            prompt_entier = (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici la réponse que tu dois reformuler : " + meilleur_reponse
            )

    # Préparer la requête API pour Gemini
    payload = {
        "contents": [{
            "parts": [{"text": prompt_entier}]  # Contenu de la demande utilisateur
        }]
    }
    headers = {
        "Content-Type": "application/json"  # Définir le type de contenu comme JSON
    }

    # Envoyer la requête POST à l'API Gemini
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:  # Si la réponse de l'API est réussie (code 200)
        # Extraire et afficher la réponse de l'API
        api_response = response.json()
        assistant_response = api_response["candidates"][0]["content"]["parts"][0]["text"]  # Récupérer la réponse du modèle assistant

        # Ajouter la réponse de l'assistant à l'historique des messages
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        # Afficher la réponse de l'assistant dans la fenêtre de chat
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    else:  # Si la réponse de l'API échoue
        error_message = f"Erreur : {response.status_code} - {response.text}"  # Message d'erreur avec statut et détails
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        # Afficher l'erreur dans la fenêtre de chat
        with st.chat_message("assistant"):
            st.markdown(error_message)
        st.error(f"Infos de débogage : {response.text}")  # Afficher les détails de l'erreur pour le débogage
