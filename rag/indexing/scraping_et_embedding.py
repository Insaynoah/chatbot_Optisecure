from bs4 import BeautifulSoup
import os
from sentence_transformers import SentenceTransformer

def lire_contrats(repertoire: str) -> dict:
    """
    Lis les fichiers HTML dans un répertoire, extrait les informations structurées et les stocke dans un dictionnaire.

    Paramètres:
        repertoire (str): Chemin vers le répertoire contenant les fichiers HTML.

    Sortie:
        dict: Un dictionnaire où les clés sont les contenus des <header> et les valeurs sont des listes de contenus des <section>, avec <ul> et <li> comme sous-sections.
    """
    # Vérifie si le répertoire existe
    if not os.path.exists(repertoire):
        print(f"Le répertoire '{repertoire}' n'existe pas.")
        return {}

    # Initialise le dictionnaire pour stocker les données
    contrats_data = {}

    # Récupère les noms des fichiers dans le répertoire
    fichiers = os.listdir(repertoire)

    for nom in fichiers:
        endroit_fichier = os.path.join(repertoire, nom)

        # Vérifie si c'est un fichier HTML
        if not nom.lower().endswith('.html'):
            print(f"Le fichier '{nom}' n'est pas un fichier HTML, il sera ignoré.")
            continue

        try:
            # Ouvre et analyse le fichier HTML
            with open(endroit_fichier, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

                # Extrait le contenu du <header>
                header = soup.find('header')
                header_text = header.get_text(strip=True) if header else f"Sans titre ({nom})"

                # Extrait les contenus des <section>
                sections = soup.find_all('section')
                sections_data = []
                for section in sections:
                    section_text = section.get_text(strip=True)
                    sub_sections = []

                    # Recherche des <ul> et <li> dans la section
                    ul_elements = section.find_all('ul')
                    for ul in ul_elements:
                        li_texts = [li.get_text(strip=True) for li in ul.find_all('li')]
                        sub_sections.append(li_texts)

                    sections_data.append({"section": section_text, "sub_sections": sub_sections})

                # Stocke les données dans le dictionnaire
                contrats_data[header_text] = sections_data

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier '{nom}': {e}")

    return contrats_data

def generer_embeddings(contrats: dict, modele: str = 'all-MiniLM-L6-v2') -> dict:
    """
    Génère des embeddings pour les données des contrats en utilisant Sentence Transformers.

    Paramètres:
        contrats (dict): Dictionnaire contenant les données des contrats.
        modele (str): Modèle Sentence Transformers à utiliser pour les embeddings.

    Sortie:
        dict: Un dictionnaire où les clés sont les headers et les valeurs sont des embeddings des sections et sous-sections.
    """
    # Charge le modèle de Sentence Transformers
    model = SentenceTransformer(modele)

    embeddings_data = {}

    for header, sections in contrats.items():
        embeddings_data[header] = []

        for section_data in sections:
            section_embedding = model.encode(section_data['section'])
            sub_section_embeddings = [model.encode(sub_section) for sub_section in section_data['sub_sections']]

            embeddings_data[header].append({
                "section_embedding": section_embedding,
                "sub_section_embeddings": sub_section_embeddings
            })

    return embeddings_data

# Exemple d'utilisation
repertoire_contrats = 'documents'
contrats = lire_contrats(repertoire_contrats)
embeddings = generer_embeddings(contrats)

# Affiche un aperçu des embeddings générés
for header, embeddings_list in embeddings.items():
    print(f"Header: {header}")
    for i, embedding_data in enumerate(embeddings_list, 1):
        print(f"  Section {i} embedding: {embedding_data['section_embedding'][:5]}... (truncated)")
        for j, sub_embedding in enumerate(embedding_data['sub_section_embeddings'], 1):
            print(f"    Sous-section {j} embedding: {sub_embedding[:5]}... (truncated)")
    print("\n" + "="*40 + "\n")
