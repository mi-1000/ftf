import os

# Chemin du dossier contenant les fichiers
folder_path = os.path.join("..", "data", "data_latin_annotated")

# Assurez-vous que le dossier existe
os.makedirs(folder_path, exist_ok=True)

# Noms des fichiers finaux
fr_output_file = os.path.join(folder_path, "fr.txt")
la_output_file = os.path.join(folder_path, "la.txt")

# Supprimer le contenu des fichiers finaux pour éviter les doublons
with open(fr_output_file, "w", encoding="utf-8") as fr_file:
    fr_file.write("")
with open(la_output_file, "w", encoding="utf-8") as la_file:
    la_file.write("")

# Parcours du dossier
for file_name in os.listdir(folder_path):
    # Vérifie si le fichier commence par "pair_Vulgate_FreSegond_1Chr", "pair_Vulgate_FreSegond_2Chr", "1Cor", "1John", "1Kgs" ou "1Pet"
    if (file_name.startswith("pair_Vulgate_FreSegond_1Sam") or 
        file_name.startswith("pair_Vulgate_FreSegond_Rev") or 
        file_name.startswith("pair_Vulgate_FreSegond_1Pet")):
        
        file_path = os.path.join(folder_path, file_name)
        
        # Ajout du contenu dans le fichier correspondant avec un saut de ligne
        if file_name.endswith("fr.txt"):
            with open(file_path, "r", encoding="utf-8") as fr_input:
                with open(fr_output_file, "a", encoding="utf-8") as fr_output:
                    fr_output.write(fr_input.read().strip() + "\n\n")
        elif file_name.endswith("la.txt"):
            with open(file_path, "r", encoding="utf-8") as la_input:
                with open(la_output_file, "a", encoding="utf-8") as la_output:
                    la_output.write(la_input.read().strip() + "\n\n")

print("Fusion des fichiers terminée.")