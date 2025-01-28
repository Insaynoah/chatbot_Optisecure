def build_prompt(prompt : str, messages : list, reponses_chroma : dict) -> str:
    """
    Construit le prompt à envoyer à l'API en fonction de l'historique des messages et des distances fournies.
    
    Cette fonction génère un prompt formaté, intégrant l'historique de la conversation, les réponses possibles basées 
    sur les distances (probabilités) et la question actuelle. Le prompt est ensuite prêt à être envoyé à l'API pour générer 
    une réponse contextuelle et adaptée.

    Args:
        prompt (str): La question ou la requête posée par l'utilisateur.
        messages (list): Liste des messages de la conversation actuelle. Chaque message doit être un dictionnaire avec 
                         des clés telles que 'role' et 'content'.
        reponses_chroma (dict): Dictionnaire contenant les distances (en tant que clés) et les réponses associées 
                                 (en tant que valeurs). Les distances sont utilisées pour déterminer la proximité 
                                 entre la question actuelle et les réponses précédentes.

    Returns:
        str: Le prompt formaté prêt à être envoyé à l'API. Ce prompt inclut l'historique de la conversation et 
             propose différentes stratégies en fonction de la question et des réponses existantes.
    """
    
    # Crée une chaîne qui représente l'historique de la conversation en format lisible
    historique = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    prompt_entier = f"Voici l'historique de la conversation :\n{historique}\n\n"

    # Trouve la distance minimale dans le dictionnaire des réponses
    min_distance = min(reponses_chroma.keys())
    threshold = 0.05  # Définit un seuil de proximité pour considérer les réponses comme proches
    # Identifie les distances proches de la distance minimale
    close_distances = [dist for dist in reponses_chroma.keys() if abs(dist - min_distance) <= threshold]

    # Si la conversation ne contient qu'un seul message (première question de l'utilisateur)
    if len(messages) == 1:
        if min_distance < 0.8:
            # Si la distance minimale est élevée, traite la question comme une demande liée aux assurances
            prompt_entier += (
                "Tu dois agir durant toute la conversation comme un agent pour une assurance : Optisecure. "
                "Si la question suivante n'a aucun sens ou est en rapport avec les assurances mais n'est pas assez détaillée, "
                "demande plus de détails/informations. Question : " + prompt
            )
        elif len(close_distances) > 1:
            # Si plusieurs réponses sont très proches de la question, propose les options à l'utilisateur
            options = "\n".join([f"Option {i + 1}: {reponses_chroma[dist]}" for i, dist in enumerate(close_distances)])
            prompt_entier += (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici plusieurs réponses possibles qui sont très proches :\n" + options + 
                "\nExplique pourquoi une réponse claire ne peut être donnée et propose une reformulation basée sur ces options."
            )
        else:
            # Sinon, retourne la meilleure réponse basée sur la distance minimale
            meilleur_reponse = reponses_chroma[min_distance]
            prompt_entier += (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici la réponse que tu dois reformuler : " + meilleur_reponse
            )
    else:
        # Si la conversation contient plusieurs messages (réponses précédentes disponibles)
        if min_distance > 0.8:
            # Si la distance est trop élevée, demande plus de détails ou réoriente la question
            prompt_entier += (
                "Si la question suivante n'est pas en rapport avec les assurances, demande de poser une question par rapport aux assurances. "
                "Sinon, demande plus de détails et ne réponds pas à la question posée. Question : " + prompt
            )
        elif len(close_distances) > 1:
            # Si plusieurs réponses sont proches, propose les options à l'utilisateur
            options = "\n".join([f"Option {i + 1}: {reponses_chroma[dist]}" for i, dist in enumerate(close_distances)])
            prompt_entier += (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici plusieurs réponses possibles qui sont très proches :\n" + options + 
                "\nExplique pourquoi une réponse claire ne peut être donnée et propose une reformulation basée sur ces options."
            )
        else:
            # Sinon, retourne la meilleure réponse basée sur la distance minimale
            meilleur_reponse = reponses_chroma[min_distance]
            prompt_entier += (
                "Voici la question posée par l'utilisateur : " + prompt + 
                " et voici la réponse que tu dois reformuler : " + meilleur_reponse
            )
    
    return prompt_entier
