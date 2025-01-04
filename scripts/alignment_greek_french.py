import xml.etree.ElementTree as ET
import os
import re

chemin = "C:/Users/Emeric/M1_TAL/Projet Transverse/ftf/data/raw/data_ancient_greek"

def extraire_fichiers_bilingues(fichier_xml):
    try:
        # Chargement du fichier XML
        tree = ET.parse(fichier_xml)
        root = tree.getroot()
        
        fichiers_grec = []
        fichiers_francais = []

        # Parcours de chaque élément <item>
        for item in root.findall('item'):
            language = item.get('language')
            filename = item.get('filename')
            bilingual = item.get('bilingual')
            # On garde uniquement les fichiers bilingues
            if bilingual == "true":
                if language == "ancient-greek":
                    fichiers_grec.append(filename)
                elif language == "french" and filename.endswith('french.txt'):
                    fichiers_francais.append(filename)

        # Associer les fichiers grec/français par leur nom de base (sans extension)
        alignements = []
        for grec in fichiers_grec:
            francais = re.sub(r"greek\.txt$", "french.txt", grec)
            alignements.append((grec, francais))
            # print(francais, grec)
        
        # for grec in fichiers_grec:
        #     base_grec = os.path.splitext(os.path.basename(grec))[0]
        #     print(base_grec)
        #     for francais in fichiers_francais:
        #         base_francais = os.path.splitext(os.path.basename(francais))[0]
        #         print(base_francais)
        #         if base_grec == base_francais:
        #             alignements.append((grec, francais))
        return alignements

    except FileNotFoundError:
        print(f"Le fichier {fichier_xml} est introuvable.")
    except ET.ParseError:
        print("Erreur de parsing XML.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

def lire_contenu_fichier(chemin):
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            contenu = f.read()
            # Nettoyage simple pour retirer les balises XML si nécessaire
            contenu = re.sub(r'<[^>]+>', '', contenu)
            return contenu.strip()
    except FileNotFoundError:
        print(f"Le fichier {chemin} est introuvable par la fonction.")
        return ""
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {chemin} : {e}")
        return ""

def segmenter_en_phrases(texte):
    # Segmenter le texte en phrases en utilisant des délimiteurs communs
    phrases = re.split(r'(?<=[.!?;])\s+', texte)
    return [phrase.strip() for phrase in phrases if phrase.strip()]

def aligner_textes(fichier_sources, dossier_sortie):
    # Extraire les paires de fichiers bilingues
    alignements = extraire_fichiers_bilingues(fichier_sources)

    print(alignements)

    if not alignements:
        print("Aucun fichier bilingue trouvé. Vérifiez le contenu de sources.xml.")
        return

    for grec, francais in alignements:
        print(f"Alignement de :\n- Texte grec : {grec}\n- Traduction française : {francais}\n")

        # Lire le contenu des fichiers grec et français
        texte_grec = lire_contenu_fichier(grec)
        texte_francais = lire_contenu_fichier(francais)

        # Segmenter les textes en phrases
        phrases_grec = segmenter_en_phrases(texte_grec)
        phrases_francais = segmenter_en_phrases(texte_francais)

        # S'assurer que les deux listes ont la même longueur
        min_len = min(len(phrases_grec), len(phrases_francais))
        phrases_grec = phrases_grec[:min_len]
        phrases_francais = phrases_francais[:min_len]

        # Créer les noms de fichiers de sortie
        nom_base = os.path.splitext(os.path.basename(grec))[0]
        fichier_grec_sortie = os.path.join(dossier_sortie, f"{nom_base}_greek.txt")
        fichier_francais_sortie = os.path.join(dossier_sortie, f"{nom_base}_french.txt")

        # Écrire les phrases grecques dans le fichier de sortie
        with open(fichier_grec_sortie, 'w', encoding='utf-8') as fg:
            fg.write("\n".join(phrases_grec))

        # Écrire les phrases françaises dans le fichier de sortie
        with open(fichier_francais_sortie, 'w', encoding='utf-8') as ff:
            ff.write("\n".join(phrases_francais))

        print(f"Fichiers créés :\n- {fichier_grec_sortie}\n- {fichier_francais_sortie}\n")

if __name__ == "__main__":
    fichier_sources = "sources/sources.xml"  # Chemin vers le fichier sources.xml
    dossier_sortie = "alignments_greek_french"   # Dossier où seront stockés les fichiers alignés


    if os.path.exists(fichier_sources):
        print(f"Le fichier {fichier_sources} existe.")
    else:
        print(f"Le fichier {fichier_sources} est introuvable.")

    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)

    aligner_textes(fichier_sources, dossier_sortie)
