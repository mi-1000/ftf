import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = "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",
)
    # api_key = os.environ.get("OPENAI_API_KEY"),

# Configurez votre clé API OpenAI

# Dossier contenant les fichiers source et celui où stocker les fichiers traduits
# source_folder = "old_french.txt"
# output_folder = "translated_files"

# Crée le dossier de sortie s'il n'existe pas
# os.makedirs(output_folder, exist_ok=True)

# Fonction pour appeler l'API OpenAI pour la traduction
def translate_text(text, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a medieval language expert, and seamlessly understand the intricate structure of Old French. Your task is to translate Old French sentences to Modern French, by analyzing their structure and finding their equivalent in word order and punctuation in Modern French. Do not respond with anything else other than the translation. Do not espond with sentences that look 'too medieval', but adapt the Modern French text into something corresponding to what one could find in contemporary writings instead. However, you should keep the same structure for the verses, i.e. each given input line should have its corresponding aligned line in your translation."},
            {"role": "user", "content": text},
        ],
        temperature=0.2,  # Réduit la créativité pour des traductions plus fidèles
    )
    return response.choices[0].message.content

# Parcourt les fichiers dans le dossier source
filename = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/AlexisProlRaM.txt'
with open(filename, 'r', encoding='utf-8') as file:
        output_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/AlexisProlRaM_translated.txt'
        
        # with open(, "r", encoding="utf-8") as file:
        text_to_translate = file.read()

        print(text_to_translate)
        
        print(f"Traduction du fichier : {filename}")
        translated_text = translate_text(text_to_translate)
        
        if translated_text:
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(translated_text)
            print(f"Traduction enregistrée dans : {output_path}")
        else:
            print(f"Échec de la traduction pour le fichier : {filename}")
