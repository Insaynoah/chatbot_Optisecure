from bs4 import BeautifulSoup
import os

def lire_contrats_avec_metadatas(repertoire: str) -> tuple:
    """
    Lis les fichiers HTML dans un répertoire, extrait uniquement la première liste (<ul> ou <ol>) de chaque section.

    Paramètres:
        repertoire (str): Chemin vers le répertoire contenant les fichiers HTML.

    Sortie:
        list: Documents extraits (contenus de la première <ul>/<ol> de chaque section).
        list: Métadonnées associées à chaque liste.
        list: Identifiants uniques pour chaque liste.
    """

    if not os.path.exists(repertoire):
        print(f"Le répertoire '{repertoire}' n'existe pas.")
        return [], [], []

    documents, metadatas, ids = [], [], []
    fichiers = os.listdir(repertoire)

    for nom in fichiers:
        chemin_fichier = os.path.join(repertoire, nom)

        if not nom.lower().endswith('.html'):
            print(f"Le fichier '{nom}' n'est pas un fichier HTML, il sera ignoré.")
            continue

        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                header = soup.find('title').get_text(strip=True) if soup.find('title') else f"Sans titre ({nom})"

                sections = soup.find_all('section')
                for i, section in enumerate(sections):
                    titre_h2 = section.find('h2').get_text(strip=True) if section.find('h2') else f"Section {i+1}"
                    titre_h3 = section.find('h3').get_text(strip=True) if section.find('h3') else "aucune"

                    # 📝 Extraction de la première liste <ul> ou <ol>
                    premiere_liste = section.find(['ul', 'ol'])
                    if premiere_liste:
                        items = [li.get_text(strip=True) for li in premiere_liste.find_all('li', recursive=False)]
                        if not items:
                            continue  # Ignore les listes vides
                        contenu_liste = ' '.join(items)

                        # 🏷️ Métadonnées
                        metadata = {
                            "source": nom,
                            "header": header,
                            "section": titre_h2,
                            "sous_section": titre_h3,
                            "type_liste": premiere_liste.name  # ul ou ol
                        }

                        # 🆔 Générer un identifiant unique pour chaque liste
                        doc_id = f"{nom}_sec_{i+1}_liste"
                        documents.append(contenu_liste)
                        metadatas.append(metadata)
                        ids.append(doc_id)

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier '{nom}': {e}")

    return documents, metadatas, ids
