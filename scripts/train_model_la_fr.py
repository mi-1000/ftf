import os
import json
from datasets import load_dataset
from transformers import MarianMTModel, MarianTokenizer, Trainer, TrainingArguments
import torch

# Variables pour les chemins de vos fichiers
source_file = 'data/data_latin_annotated/la.txt'  # fichier contenant le texte en latin (source)
target_file = 'data/data_latin_annotated/fr.txt'  # fichier contenant la traduction en français (cible)

# Balises de langue pour le modèle MarianMT
lang_tags = {
    "fr": ">>fr<<",
    "la": ">>la<<"
}

# Charger les données avec les balises de langue appropriées pour la direction Latin -> Français
def load_data(source_file, target_file, lang_tags):
    with open(source_file, 'r', encoding='utf-8') as f:
        source_text = f.readlines()
    with open(target_file, 'r', encoding='utf-8') as f:
        target_text = f.readlines()
    
    # Ajouter les paires pour la direction Latin -> Français
    data = [{"text": f"{lang_tags['fr']} {src.strip()}", "translation": tgt.strip()} for src, tgt in zip(source_text, target_text)]
    
    return data

# Charger les données
print("[INFO] Chargement des données...")
data = load_data(source_file, target_file, lang_tags)

# Enregistrer les données sous forme de fichier JSON
json_file = 'data.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print(f"[INFO] Données enregistrées dans {json_file}")

# Charger les données dans le dataset
# En utilisant le format JSON à partir du fichier préparé
print("[INFO] Chargement du dataset...")
dataset = load_dataset('json', data_files={'train': json_file}, split='train')

# Charger le tokenizer pour le modèle MarianMT
print("[INFO] Chargement du tokenizer...")
tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ROMANCE-en')

# Fonction de tokenisation
def tokenize_function(examples):
    model_inputs = tokenizer(examples["text"], padding="max_length", truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["translation"], padding="max_length", truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Appliquer la tokenisation sur le dataset
print("[INFO] Application de la tokenisation sur le dataset...")
tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Charger le modèle MarianMT pour le fine-tuning dans la direction Latin -> Français
print("[INFO] Chargement du modèle MarianMT pour le fine-tuning...")
model_la_fr = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ROMANCE-en')

# Geler les premières couches du modèle pour préserver les caractéristiques linguistiques de base
print("[INFO] Gel des premières couches du modèle...")
for param in model_la_fr.model.encoder.parameters():
    param.requires_grad = False

# Configuration des arguments d'entraînement
print("[INFO] Configuration des arguments d'entraînement...")
training_args_la_fr = TrainingArguments(
    output_dir='./results_la_fr',              # répertoire pour sauvegarder les résultats
    evaluation_strategy="epoch",       # évaluer à la fin de chaque époque
    learning_rate=1e-5,                  # taux d'apprentissage
    per_device_train_batch_size=4,       # taille du batch d'entraînement
    num_train_epochs=3,                  # nombre d'époques
    logging_dir='./logs_la_fr',          # répertoire pour les logs
    logging_steps=10,                    # log toutes les 10 étapes
)

# Initialisation du Trainer pour la direction Latin -> Français
print("[INFO] Initialisation du Trainer...")
trainer_la_fr = Trainer(
    model=model_la_fr,
    args=training_args_la_fr,
    train_dataset=tokenized_datasets,
    eval_dataset=tokenized_datasets,  # vous pouvez utiliser un jeu de données de validation séparé si vous en avez
)

# Lancer l'entraînement pour la direction Latin -> Français
print("[INFO] Début de l'entraînement...")
trainer_la_fr.train()

# Sauvegarder le modèle fine-tuné pour la direction Latin -> Français
output_dir_la_fr = './finetuned_model_la_fr'
model_la_fr.save_pretrained(output_dir_la_fr)
tokenizer.save_pretrained(output_dir_la_fr)

print(f"[INFO] Modèle et tokenizer pour Latin -> Français sauvegardés dans {output_dir_la_fr}")
