import os
from transformers import MarianMTModel, MarianTokenizer

# Variables pour les chemins de vos fichiers
model_dir = '../models/la_fr_01'  # répertoire contenant le modèle MarianMT fine-tuné
input_file = './test_model_files/fr-la/fr_la-fr.txt'  # fichier contenant le texte en français
output_file = './test_model_files/fr-la/fr_to_la-marianmt01.txt'  # fichier pour sauvegarder les traductions en latin

# Charger le modèle et le tokenizer fine-tunés
print("[INFO] Chargement du modèle MarianMT fine-tuné...")
model = MarianMTModel.from_pretrained(model_dir)
tokenizer = MarianTokenizer.from_pretrained(model_dir)

# Lire les lignes du fichier de texte en latin
print("[INFO] Lecture du fichier en français...")
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Traduire chaque ligne du français vers le latin
print("[INFO] Traduction des lignes...")
translations = []
for line in lines:
    if line.strip():  # Ignorer les lignes vides
        # Préparer l'entrée avec la balise de langue cible
        inputs = tokenizer(f">>fr<< {line.strip()}", return_tensors="pt", padding=True, truncation=True)
        # Générer la traduction
        translated_tokens = model.generate(**inputs)
        # Décoder la traduction
        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        translations.append(translated_text)

# Sauvegarder les traductions dans un fichier de sortie
print("[INFO] Sauvegarde des traductions...")
with open(output_file, 'w', encoding='utf-8') as f:
    for translation in translations:
        f.write(translation + "\n")

print(f"[INFO] Traductions sauvegardées dans {output_file}")
