import chromadb
from sentence_transformers import SentenceTransformer
from embedding import generer_embeddings_avec_metadatas
from scraping import lire_contrats_avec_metadatas

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Fonction pour insérer dans ChromaDB
def inserer_dans_chromadb(embeddings_data):
    """
    Insère les données dans la base vectorielle chromaDB.

    Paramètres:
        embeddings_data (dict): dictionnaire d'id qui prennent en valeur un dictionnaire de metadatas, documents et embeddings

    Sortie:
        Arrête la fonction si la collection existe déjà.
        Sinon, insère les données dans une nouvelle collection.
    """
    # Créer ou se connecter à une base ChromaDB existante
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    client = chromadb.Client()

    # Nom de la collection
    collection_name = "contrats_collection"

    # Vérifier si la collection existe déjà
    existing_collections = [col.name for col in client.list_collections()]
    if collection_name in existing_collections:
        print(f"La collection '{collection_name}' existe déjà. Aucun ajout effectué.")
        return  # Arrêter la fonction si la collection existe

    # Créer une nouvelle collection
    collection = client.create_collection(name=collection_name)

    # Insertion des documents, embeddings et métadonnées dans ChromaDB
    for doc_id, data in embeddings_data.items():
        collection.add(
            ids=[doc_id],                  # Liste des IDs
            embeddings=[data["embedding"]], # Liste des embeddings
            metadatas=[data["metadata"]],   # Liste des métadonnées
            documents=[data["documents"]]  # Liste des documents (texte de la section)
        )

 


# Exemple d'utilisation

# 📂 Remplace par ton chemin de répertoire contenant les fichiers HTML
repertoire_html = "./documents"

# Lire les documents, métadonnées, et ids
documents, metadatas, ids = lire_contrats_avec_metadatas(repertoire_html)

# 🚀 Générer les embeddings
embeddings_contrats = generer_embeddings_avec_metadatas(documents, metadatas, ids)



print("Documents et embeddings insérés dans ChromaDB avec succès!")


def requete_chromadb(question, collection_name="contrats_collection", modele="all-MiniLM-L6-v2"):
    """
    Effectue une requête sur la base de données et compare la similarité entre la question et les documents

    Paramètres:
        question (str): question posé par l'utilisateur
        collection_name (str): par défaut le nom de la collection
        modele (): model d'embedding
    Sortie:
        Création de la collection
    """
    # Créer ou se connecter à une base ChromaDB existante
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    # 🗂 Insertion dans ChromaDB
    inserer_dans_chromadb(embeddings_contrats)
    client = chromadb.Client()

    # Charger la collection existante
    collection = client.get_collection(name=collection_name)

    # Générer l'embedding de la question avec le modèle SentenceTransformer
    model = SentenceTransformer(modele)
    question_embedding = model.encode(question)

    # Effectuer la requête en utilisant l'embedding de la question
    results = collection.query(
        query_embeddings=[question_embedding],  # Embedding de la question
        n_results=5  # Nombre de résultats souhaités
    )
    
    return results
