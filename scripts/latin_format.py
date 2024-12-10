import os
from cltk.alphabet.lat import JVReplacer, LigatureReplacer, remove_accents, remove_macrons, swallow_angle_brackets, normalize_lat

# Chemin vers le fichier d'entrée et de sortie
input_file = "data/data_latin_annotated/la.txt"
output_file = "data/data_latin_annotated/la_formatted.txt"

# Vérifier si le fichier source existe
if not os.path.exists(input_file):
    print(f"Le fichier '{input_file}' n'existe pas.")
    exit()

# Lire le contenu du fichier la.txt
with open(input_file, "r", encoding="utf-8") as file:
    latin_text = file.read()

# Initialiser les remplaçants
jv_replacer = JVReplacer()
ligature_replacer = LigatureReplacer()

# Appliquer les transformations
# 1. Remplacer J/V par I/U
latin_text = jv_replacer.replace(latin_text)

# 2. Remplacer les ligatures œ/æ par oe/ae
latin_text = ligature_replacer.replace(latin_text)

# 3. Supprimer les accents
latin_text = remove_accents(latin_text)

# 4. Supprimer les macrons
latin_text = remove_macrons(latin_text)

# 5. Supprimer le texte entre crochets angulaires et les crochets eux-mêmes
latin_text = swallow_angle_brackets(latin_text)

# 6. Normaliser entièrement (par sécurité)
latin_text = normalize_lat(latin_text, drop_accents=True, drop_macrons=True, jv_replacement=True, ligature_replacement=True)

# Écrire le texte transformé dans un nouveau fichier
with open(output_file, "w", encoding="utf-8") as file:
    file.write(latin_text)

print(f"Le texte latin a été formaté et sauvegardé dans '{output_file}'.")
