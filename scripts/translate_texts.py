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

def split_text_into_chunks(text, max_tokens):
    """
    Splits the input text into smaller chunks, ensuring each chunk has no more than max_tokens.
    """
    words = text.split()  # Tokenize the text based on whitespace
    chunks = []
    current_chunk = []
    current_length = 0  # Tracks the cumulative length of the current chunk

    for word in words:
        word_length = len(word) + 1  # Include the space after each word
        if current_length + word_length > max_tokens:
            # Save the current chunk and start a new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            # Add the word to the current chunk
            current_chunk.append(word)
            current_length += word_length

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def process_folder(folder_path):
    """
    Process all XML files in a folder.   
    """
    print("searching for files...")
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            with open(folder_path+file_name, 'r', encoding='utf-8') as file:\
        
                text_to_translate = file.read()

                print(f"Original text length: {len(text_to_translate)} characters")
                print(f"Processing file: {file_name}")

                # Split text into chunks if needed
                max_tokens = 1000
                chunks = split_text_into_chunks(text_to_translate, max_tokens)

                print(f"Text split into {len(chunks)} chunk(s).")

                # Translate each chunk
                translated_chunks = []
                for i, chunk in enumerate(chunks, start=1):
                    print(f"Translating chunk {i}/{len(chunks)}...")
                    translated_chunk = translate_text(chunk)
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        print(f"Translation failed for chunk {i}.")
                        break

                # Combine translated chunks
                translated_text = " ".join(translated_chunks)
                
                output_path = folder_path + f"{os.path.splitext(file_name)[0]}_translated.txt"

                if translated_text:
                    with open(output_path, "w", encoding="utf-8") as output_file:
                        output_file.write(translated_text)
                    print(f"Traduction enregistrée dans : {output_path}")
                else:
                    print(f"Échec de la traduction pour le fichier : {file_name}")

print("start process...")
folder_path = 'C:/Bureau/Master/S7/project/ftf/data/raw/data_old_french/done/'
process_folder(folder_path)