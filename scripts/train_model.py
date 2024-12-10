
# #source_file = 'data/data_latin_annotated/la.txt'  # fichier contenant le texte en latin
# #target_file = 'data/data_latin_annotated/fr.txt'  # fichier contenant la traduction en français

# import os
# import json
# from datasets import load_dataset
# from transformers import MarianMTModel, MarianTokenizer, Trainer, TrainingArguments

# # Variables pour les chemins de vos fichiers
# source_file = 'data/data_latin_annotated/la.txt'  # fichier contenant le texte en latin
# target_file = 'data/data_latin_annotated/fr.txt'  # fichier contenant la traduction en français

# # Langues source et cible
# lang1 = "ROMANCE"
# lang2 = "en"

# # Charger les données
# def load_data(source_file, target_file):
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_text = f.readlines()
#     with open(target_file, 'r', encoding='utf-8') as f:
#         target_text = f.readlines()
    
#     # Créer une liste de dictionnaires avec les paires de texte source et cible
#     data = [{"text": src.strip(), "translation": tgt.strip()} for src, tgt in zip(source_text, target_text)]
    
#     return data

# # Charger les données dans Hugging Face Dataset (format JSON)
# data = load_data(source_file, target_file)

# # Enregistrer les données sous forme de fichier JSON
# json_file = 'data.json'
# with open(json_file, 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

# # Charger les données dans le dataset
# dataset = load_dataset('json', data_files={'train': json_file}, split='train')

# # Charger les tokenizers
# tokenizer_1 = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{lang2}-{lang1}')
# tokenizer_2 = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{lang1}-{lang2}')

# # Fonction de tokenisation
# def tokenize_function(examples):
#     model_inputs = tokenizer_1(examples["text"], padding="max_length", truncation=True)
#     with tokenizer_2.as_target_tokenizer():
#         labels = tokenizer_2(examples["translation"], padding="max_length", truncation=True)
#     model_inputs["labels"] = labels["input_ids"]
#     return model_inputs

# # Appliquer la tokenisation sur le dataset
# tokenized_datasets = dataset.map(tokenize_function, batched=True)

# # Charger le modèle MarianMT
# model = MarianMTModel.from_pretrained(f'Helsinki-NLP/opus-mt-{lang1}-{lang2}')

# # Configuration des arguments d'entraînement
# training_args = TrainingArguments(
#     output_dir='./results',              # répertoire pour sauvegarder les résultats
#     evaluation_strategy="epoch",         # évaluer à la fin de chaque époque
#     learning_rate=2e-5,                  # taux d'apprentissage
#     per_device_train_batch_size=8,       # taille du batch d'entraînement
#     num_train_epochs=3,                  # nombre d'époques
#     logging_dir='./logs',                # répertoire pour les logs
#     logging_steps=10,                    # log toutes les 10 étapes
# )

# # Initialisation du Trainer
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized_datasets,
#     eval_dataset=tokenized_datasets,  # vous pouvez utiliser un jeu de données de validation séparé si vous en avez
# )

# # Lancer l'entraînement
# trainer.train()

# # Sauvegarder le modèle fine-tuné
# output_dir = './finetuned_model'
# model.save_pretrained(output_dir)
# tokenizer_1.save_pretrained(output_dir)
# tokenizer_2.save_pretrained(output_dir)

# print(f"Modèle et tokenizer sauvegardés dans {output_dir}")

import os
import json
import random
from datasets import load_dataset
from transformers import MarianMTModel, MarianTokenizer, Trainer, TrainingArguments
import torch

# Variables pour les chemins de vos fichiers
source_file = 'la.txt' # 'data/data_latin_annotated/la.txt'  # fichier contenant le texte en latin (source)
target_file = 'fr.txt'  # 'data/data_latin_annotated/fr.txt'  # fichier contenant la traduction en français (cible)

# Balises de langue pour le modèle MarianMT
lang_tags = {
    "fr": ">>fr<<",
    "la": ">>la<<"
}

# Charger les données avec les balises de langue appropriées pour les deux directions
def load_data_bidirectional(source_file, target_file, lang_tags):
    with open(source_file, 'r', encoding='utf-8') as f:
        source_text = f.readlines()
    with open(target_file, 'r', encoding='utf-8') as f:
        target_text = f.readlines()
    
    # Ajouter les paires dans les deux directions
    data = []
    for src, tgt in zip(source_text, target_text):
        # Latin vers Français
        data.append({"text": f"{lang_tags['fr']} {src.strip()}", "translation": tgt.strip()})
        # Français vers Latin
        data.append({"text": f"{lang_tags['la']} {tgt.strip()}", "translation": src.strip()})
    
    return data

# Charger les données en bidirectionnel
print("[INFO] Chargement des données...")
data = load_data_bidirectional(source_file, target_file, lang_tags)

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

# Liste des hyperparamètres à tester
learning_rates = [1e-5, 2e-5, 5e-5]
batch_sizes = [4, 8, 16]
num_epochs = [3, 5]

# Boucle pour tester différentes combinaisons d'hyperparamètres
best_loss = float('inf')
best_params = {}

for learning_rate in learning_rates:
    for batch_size in batch_sizes:
        for num_epoch in num_epochs:
            print(f"[INFO] Testing combination: learning_rate={learning_rate}, batch_size={batch_size}, num_epochs={num_epoch}")
            
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
                output_dir=f'./results_la_fr_lr{learning_rate}_bs{batch_size}_ep{num_epoch}',
                evaluation_strategy="epoch",       # évaluer à la fin de chaque époque
                learning_rate=learning_rate,         # taux d'apprentissage
                per_device_train_batch_size=batch_size,  # taille du batch d'entraînement
                num_train_epochs=num_epoch,          # nombre d'époques
                logging_dir=f'./logs_la_fr_lr{learning_rate}_bs{batch_size}_ep{num_epoch}',  # répertoire pour les logs
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

            # Obtenir la perte (loss) après l'entraînement
            print("[INFO] Évaluation du modèle...")
            eval_results = trainer_la_fr.evaluate()
            eval_loss = eval_results['eval_loss']
            print(f"[INFO] Eval Loss: {eval_loss}")

            # Sauvegarder les hyperparamètres si la perte est la plus basse
            if eval_loss < best_loss:
                best_loss = eval_loss
                best_params = {
                    "learning_rate": learning_rate,
                    "batch_size": batch_size,
                    "num_epochs": num_epoch
                }

print(f"[INFO] Best parameters found: {best_params} with eval_loss={best_loss}")

# Sauvegarder les paramètres optimaux
with open('best_hyperparameters.json', 'w') as f:
    json.dump(best_params, f, indent=4)
print("[INFO] Paramètres optimaux enregistrés dans best_hyperparameters.json")

# Charger le modèle MarianMT pour le fine-tuning final avec les meilleurs hyperparamètres
print("[INFO] Chargement du modèle pour le fine-tuning final avec les meilleurs hyperparamètres...")
best_learning_rate = best_params['learning_rate']
best_batch_size = best_params['batch_size']
best_num_epochs = best_params['num_epochs']

model_fr_la = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ROMANCE-en')

# Geler les premières couches du modèle pour préserver les caractéristiques linguistiques de base
print("[INFO] Gel des premières couches du modèle pour le fine-tuning final...")
for param in model_fr_la.model.encoder.parameters():
    param.requires_grad = False

# Configuration des arguments d'entraînement avec les meilleurs hyperparamètres
print("[INFO] Configuration des arguments d'entraînement avec les meilleurs hyperparamètres...")
training_args_fr_la = TrainingArguments(
    output_dir='./results_fr_la_best',              # répertoire pour sauvegarder les résultats
    evaluation_strategy="epoch",       # évaluer à la fin de chaque époque
    learning_rate=best_learning_rate,    # meilleur taux d'apprentissage
    per_device_train_batch_size=best_batch_size,  # meilleure taille du batch d'entraînement
    num_train_epochs=best_num_epochs,    # meilleur nombre d'époques
    logging_dir='./logs_fr_la_best',                # répertoire pour les logs
    logging_steps=10,                    # log toutes les 10 étapes
)

# Initialisation du Trainer pour la direction Français -> Latin avec les meilleurs hyperparamètres
print("[INFO] Initialisation du Trainer pour le fine-tuning final...")
trainer_fr_la = Trainer(
    model=model_fr_la,
    args=training_args_fr_la,
    train_dataset=tokenized_datasets,
    eval_dataset=tokenized_datasets,  # vous pouvez utiliser un jeu de données de validation séparé si vous en avez
)

# Lancer l'entraînement pour la direction Français -> Latin avec les meilleurs hyperparamètres
print("[INFO] Début de l'entraînement final...")
trainer_fr_la.train()

# Sauvegarder le modèle fine-tuné pour la direction Français -> Latin
output_dir_fr_la = './finetuned_model_fr_la_best'
model_fr_la.save_pretrained(output_dir_fr_la)
tokenizer.save_pretrained(output_dir_fr_la)

print(f"[INFO] Modèle et tokenizer pour Français -> Latin sauvegardés dans {output_dir_fr_la}")
