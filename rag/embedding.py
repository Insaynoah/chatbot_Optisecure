from sentence_transformers import SentenceTransformer

def generer_embeddings_avec_metadatas(documents, metadatas, ids, modele: str = 'all-MiniLM-L6-v2') -> dict:
    """
    Génère des embeddings pour les documents en utilisant Sentence Transformers.
    
    Paramètres:
        documents (list): Liste des textes (sections et sous-sections).
        metadatas (list): Liste des métadonnées associées à chaque document.
        ids (list): Liste des identifiants uniques des documents.
        modele (str): Modèle Sentence Transformers à utiliser pour les embeddings.

    Sortie:
        dict: Dictionnaire où les clés sont les IDs des documents, et les valeurs sont des embeddings et métadonnées.
    """
    # Charge le modèle de Sentence Transformers
    model = SentenceTransformer(modele)

    embeddings_data = {}

    # Parcours chaque document
    for doc_text, metadata, doc_id in zip(documents, metadatas, ids):
        # Génère l'embedding pour le texte du document
        document_embedding = model.encode(doc_text)
        # Stocke l'embedding et les métadonnées
        embeddings_data[doc_id] = {
            "embedding": document_embedding,
            "metadata": metadata,
            "documents":doc_text
        }

    return embeddings_data