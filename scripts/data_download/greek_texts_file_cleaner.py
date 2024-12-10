import os
import glob
import re
from langdetect import detect

# Specify the directory containing the text files
directory_path = 'C:/Bureau/Master/S7/project/greek_text'  # Change this to your directory path

# Use glob to find all text files in the directory
text_files = glob.glob(os.path.join(directory_path, '*.txt'))   

# Function to check if the text is in English
def is_text_english(text):
    try:
        language = detect(text)
        return language == 'en'
    except:
        return False

# Function to clean the content based on the given patterns
def clean_content(content):
    # Remove "LIVRE + number" (e.g., LIVRE 1)
    # content = re.sub(r'\bLIVRE\s*\d+\b', '', content)

    # # Remove "CHAPITRE + number or Roman numeral" (e.g., CHAPITRE 5, CHAPITRE V)
    content = re.sub(r'\bChapitre\s*(\d+|[IVXLCDM]+)\b', '', content)

    # # Remove lines that start with "Roman numeral+." (e.g., I., IV., X.)
    # content = re.sub(r'^[IVXLCDM]+\.\s*', '', content, flags=re.MULTILINE)

    # # Remove the pattern "§ 1." or similar (section symbols)
    # content = re.sub(r'§\s*\d+\.+', '', content)

    content = re.sub(r'§\s*\d+\s*\.*', '', content)
    # This regex removes patterns like "§ 3 ." or "§ 4"

    content = re.sub(r'^[A-Z]{5,}.*$', '', content, flags=re.MULTILINE)
    # This regex removes lines that start with 5 or more uppercase characters

    # # Remove lines that start with "Number+." (e.g., 1., 2., etc.)
    content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)

    # # Remove patterns like "<number>" (e.g., <5>)
    content = re.sub(r'<\d+>', '', content)

    # # Remove patterns like "<letters>" (e.g., <abc>)
    content = re.sub(r'<[a-zA-Z]+>', '', content)

    # # Remove the symbol "—" (em dash)
    content = content.replace('—', '')

    # # Remove the symbol "-" (hyphen)
    # content.replace('-', '')

    # # Remove "Chap. XXIII." (e.g., Chap. XXIII.)
    content = re.sub(r'\bChap\.\s*[IVXLCDM]+', '', content)

    # # Remove lines that start with "number space" or "number dot" (e.g., "1 ", "1.")
    # content = re.sub(r'^\d+[\s\.]', '', content, flags=re.MULTILINE)

    # # Remove lines that contain only dots (e.g., "...")
    # content = re.sub(r'^\.+$', '', content, flags=re.MULTILINE)

    # # Remove lines that start with a dot (e.g., ". Something")
    # content = re.sub(r'^\.\s*', '', content, flags=re.MULTILINE)

    # # Remove spaces and tabs at the start of lines
    # content = re.sub(r'^[ \t]+', '', content, flags=re.MULTILINE)

    # # Remove "LIVRE V." or "LETTRE XIII." (e.g., LIVRE followed by Roman numeral, LETTRE followed by Roman numeral)
    # content = re.sub(r'\b(LIVRE|LETTRE)\s+[IVXLCDM]+\.\b', '', content)

    # # Remove "QUESTION XV." or similar (e.g., QUESTION followed by Roman numerals)
    # content = re.sub(r'\bQUESTION\s+[IVXLCDM]+\.\b', '', content)

    content = re.sub(r'ΚΕΦΑΛΑΙΟΝ\s*[Α-Ω]{1,3}\'\.', '', content)
    # This regex removes patterns like "ΚΕΦΑΛΑΙΟΝ ΛΘ'." where "ΚΕΦΑΛΑΙΟΝ" is followed by Greek numerals and an apostrophe

    content = re.sub(r'\s\d+\.\s', '', content)
    # This regex removes patterns like "number." where "number" is a sequence of digits followed by a period

    content = re.sub(r'^ΚΕΦΑΛΑΙΟΝ.*$', '', content, flags=re.MULTILINE)
    # This regex removes lines that start with "ΚΕΦΑΛΑΙΟΝ"

    # Remove alinéas at the beginning of paragraphs (empty line + tab or spaces)
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)

    content = re.sub(r'<[^>]{1,4}>\s*', '', content)

    content = re.sub(r'\{[^\}]{1,2}\}', '', content)
    # This regex removes patterns like "{Δ.}" or "{}"

    return content

# Loop through each text file, clean its content, and write back to the file
# Your existing code with added logic to delete English files
for file_path in text_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Check if the content is in English
    # if is_text_english(content):
        # If content is in English, delete the file
        # os.remove(file_path)
        # print(f"Deleted {file_path} (English content detected)")
    # else:
        # Clean the content if it's not in English
        cleaned_content = clean_content(content)

        # Write the cleaned content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        print(f"Cleaned and wrote to {file_path}")



# import os
# import glob
# import xml.etree.ElementTree as ET

# # Spécifiez le répertoire contenant les fichiers texte
# source_directory_path = 'C:/Bureau/Master/S7/project/greek_text'  # Remplacez par le chemin de votre répertoire source
# # Spécifiez le répertoire où enregistrer les fichiers XML
# destination_directory_path = 'C:/Bureau/Master/S7/project/xml_greek_text'  # Remplacez par le chemin du répertoire de destination

# # Créez le répertoire de destination s'il n'existe pas
# os.makedirs(destination_directory_path, exist_ok=True)

# # Fonction pour convertir le contenu en XML
# def convert_to_xml(file_name, content):
#     # Créer un élément racine nommé "document"
#     root = ET.Element("document")
    
#     # Ajouter un élément pour le nom du fichier
#     title_element = ET.SubElement(root, "title")
#     title_element.text = file_name

#     # Ajouter un élément pour le contenu du fichier
#     content_element = ET.SubElement(root, "content")
#     content_element.text = content

#     # Retourner l'arbre XML
#     return ET.ElementTree(root)

# # Parcourir chaque fichier texte et créer une version XML dans le répertoire de destination
# text_files = glob.glob(os.path.join(source_directory_path, '*.txt'))

# for file_path in text_files:
#     file_name = os.path.basename(file_path).replace('.txt', '')
    
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
    
#     # Convertir le contenu en XML
#     xml_tree = convert_to_xml(file_name, content)

#     # Définir le nom de fichier pour la version XML dans le répertoire de destination
#     xml_file_path = os.path.join(destination_directory_path, f"{file_name}.xml")

#     # Sauvegarder le fichier XML dans le dossier de destination
#     xml_tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    
#     print(f"Fichier XML créé dans {xml_file_path}")
