import streamlit as st
from modules.feedback import save_feedback
from modules.prompt_builder import build_prompt
import requests
import json
from modules.bdd import requete_chromadb

# Configuration de la page
st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Lecture de la clé API depuis un fichier local pour accéder à l'API de génération de contenu
with open('cleApi.txt', 'r') as file:
    api_key = file.read().strip()

# URL de l'API de génération de contenu de Google
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

# Initialisation des variables de session pour stocker la note et les messages
if "rating" not in st.session_state:
    st.session_state['rating'] = 0  # Note de l'utilisateur
if "messages" not in st.session_state:
    st.session_state.messages = []  # Historique des messages de la conversation

# Affichage du logo et du titre de l'application Streamlit
st.logo(icon_image='https://i.ibb.co/MSZB1qp/Marceline-1.png', image='https://i.ibb.co/MSZB1qp/Marceline-1.png', size='large')
st.title("Chatbot OptiSecure Assurances")

# Sidebar pour soumettre une évaluation
with st.sidebar:
    st.subheader("💬 Évaluez la réponse de l'assistant (0 à 5)")
    rating = st.slider("⭐ Sélectionnez une note", min_value=0, max_value=5, step=1, key="rating")  # Sélection de la note
    if st.button("🔍 Soumettre l'évaluation"):  # Bouton pour soumettre l'évaluation
        chat_history = " ".join([msg["content"] for msg in st.session_state.messages])  # Historique de la conversation
        save_feedback(rating, chat_history)  # Sauvegarde de l'évaluation dans le fichier
        st.write(f"👍 Merci pour votre évaluation : {rating}")  # Affichage de la confirmation de l'évaluation

# Zone de saisie pour la question de l'utilisateur
prompt = st.chat_input("Que voulez-vous savoir sur les contrats d'OptiSecure Assurances ?")

# Affichage de l'historique des messages de la conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Si un prompt est saisi, traiter la requête
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})  # Ajouter le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)  # Afficher la question de l'utilisateur

    # Recherche des réponses les plus proches dans la base de données à l'aide de ChromaDB
    reponses_chroma = requete_chromadb(prompt)
    reponses_chroma = dict(zip(reponses_chroma['distances'][0], reponses_chroma['documents'][0]))  # Conversion des réponses en dictionnaire

    # Construction du prompt pour l'API avec l'historique et les réponses proches
    prompt_entier = build_prompt(prompt, st.session_state.messages, reponses_chroma)

    # Préparation de la requête à l'API
    payload = {"contents": [{"parts": [{"text": prompt_entier}]}]}
    headers = {"Content-Type": "application/json"}

    # Envoi de la requête à l'API de génération de contenu
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Traitement de la réponse de l'API
    if response.status_code == 200:  # Si la requête a réussi
        api_response = response.json()  # Extraction des données de la réponse JSON
        assistant_response = api_response["candidates"][0]["content"]["parts"][0]["text"]  # Réponse de l'assistant
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})  # Ajouter la réponse à l'historique
        with st.chat_message("assistant"):
            st.markdown(assistant_response)  # Afficher la réponse de l'assistant
    else:  # En cas d'erreur
        error_message = f"Erreur : {response.status_code} - {response.text}"  # Message d'erreur
        st.session_state.messages.append({"role": "assistant", "content": error_message})  # Ajouter l'erreur à l'historique
        with st.chat_message("assistant"):
            st.markdown(error_message)  # Afficher l'erreur à l'utilisateur
        st.error(f"Infos de débogage : {response.text}")  # Afficher les détails d'erreur pour le débogage
