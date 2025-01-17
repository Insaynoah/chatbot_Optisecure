import streamlit as st

USERS = {"admin": "admin"}

def authenticate_user() -> bool:
    """
    Authentifie l'utilisateur.

    Returns:
        bool: True si l'utilisateur est authentifié, False sinon.
    """
    # Vérification si l'utilisateur est déjà authentifié dans la session
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False  # Initialisation de l'état d'authentification

    # Si l'utilisateur n'est pas encore authentifié
    if not st.session_state["authenticated"]:
        st.title("🔒 Authentification requise")  # Affichage du titre pour l'authentification
        # Demande du nom d'utilisateur et du mot de passe
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")  # Mot de passe masqué

        # Vérification des informations de connexion lors du clic sur le bouton
        if st.button("Se connecter"):
            # Si le nom d'utilisateur et le mot de passe sont valides, authentification réussie
            if username in USERS and USERS[username] == password:
                st.session_state["authenticated"] = True  # Marquer l'utilisateur comme authentifié
                st.success("Connexion réussie ! Accédez au dashboard en recliquant sur le bouton Dashboard")  # Message de succès
            else:
                # Si les informations sont incorrectes, afficher un message d'erreur
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
        return False  # Retourne False pour indiquer que l'utilisateur n'est pas authentifié

    return True  # Retourne True si l'utilisateur est authentifié
