def build_prompt(prompt: str, messages: list, reponses_chroma: dict) -> str:
    """
    Construit le prompt à envoyer à l'API en fonction de l'historique des messages et des réponses possibles.
    
    Désormais, toutes les réponses contenues dans reponses_chroma sont incluses dans le prompt, 
    sans sélection basée sur la distance. L'agent (Optisecure) devra choisir la meilleure réponse 
    parmi l'ensemble des possibilités fournies.
    
    Args:
        prompt (str): La question ou la requête posée par l'utilisateur.
        messages (list): Liste des messages de la conversation actuelle. Chaque message doit être 
                         un dictionnaire avec des clés telles que 'role' et 'content'.
        reponses_chroma (dict): Dictionnaire contenant différentes réponses (valeurs) 
                                indexées par une distance (clés). Ici, toutes les réponses 
                                seront directement incluses dans le prompt.
    
    Returns:
        str: Le prompt formaté prêt à être envoyé à l'API.
    """

    # Si reponses_chroma est vide, signale qu'aucune réponse n'est trouvée.
    if not reponses_chroma:
        prompt_entier = (
            "Tu dois agir comme un agent pour une assurance : Optisecure.\n"
            f"Question : {prompt}\n(Note: Aucune réponse trouvée dans reponses_chroma.)"
        )
        return prompt_entier

    # Prépare toutes les réponses possibles dans une liste.
    all_responses = list(reponses_chroma.values())
    all_responses_formatted = "\n".join(
        [f"- Possibilité {i+1}: {resp}" for i, resp in enumerate(all_responses)]
    )

    # Si c'est le premier message, inclure l'historique de la conversation.
    if len(messages) == 1:
        historique = f"{messages[0]['role']}: {messages[0]['content']}"
        prompt_entier = (
            "Tu dois agir comme un agent pour une assurance : Optisecure.\n"
            f"Historique de la conversation :\n{historique}\n\n"
            f"Voici la question posée par l'utilisateur : {prompt}\n\n"
            "Voici toutes les réponses possibles que nous avons trouvées :\n"
            f"{all_responses_formatted}\n\n"
            "Choisis et reformule la meilleure réponse à fournir, en fonction du contexte.\n"
        )
    else:
        prompt_entier = (
            f"Voici la question posée par l'utilisateur : {prompt}\n\n"
            "Voici toutes les réponses possibles que nous avons trouvées :\n"
            f"{all_responses_formatted}\n\n"
            "Choisis et reformule la meilleure réponse à fournir, en fonction du contexte.\n"
        )

    return prompt_entier