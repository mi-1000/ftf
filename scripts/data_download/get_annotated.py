import os
import shutil
import xml.etree.ElementTree as ET

# Chemins des dossiers
source_xml = os.path.abspath("sources/sources.xml")
source_folder = "data/data_latin"
destination_folder = "data/data_latin_annotated"

# Créer le dossier de destination s'il n'existe pas
os.makedirs(destination_folder, exist_ok=True)

# Parse le fichier XML
tree = ET.parse(source_xml)
root = tree.getroot()

# Convertir les éléments XML en une liste pour accéder aux lignes précédentes
items = list(root.findall("item"))

# Parcours des éléments <item> dans le fichier XML
for i, item in enumerate(items):
    language = item.get("language")
    bilingual = item.get("bilingual")
    filename = item.get("filename")

    # Vérifie les critères pour "latin" et "bilingual=true"
    if language == "latin" and bilingual == "true":
        # Construit le chemin source et destination du fichier actuel
        source_file = filename

        destination_file = os.path.join(destination_folder, os.path.basename(filename))

        # Copie le fichier actuel si celui-ci existe dans le dossier source
        if os.path.exists(source_file):
            shutil.copy2(source_file, destination_file)
            print(f"Fichier copié : {source_file} vers {destination_file}")
        else:
            print(f"Fichier introuvable : {source_file}")

        # Copier également le fichier de la ligne précédente s'il existe
        if i > 0:  # Vérifie qu'il y a une ligne précédente
            prev_filename = items[i - 1].get("filename")
            prev_source_file = prev_filename
            prev_destination_file = os.path.join(destination_folder, os.path.basename(prev_filename))

            if os.path.exists(prev_source_file):
                shutil.copy2(prev_source_file, prev_destination_file)
                print(f"Fichier copié : {prev_source_file} vers {prev_destination_file}")
            else:
                print(f"Fichier introuvable : {prev_source_file}")
