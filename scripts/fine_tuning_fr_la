from datasets import load_dataset
from transformers import MarianTokenizer, MarianMTModel
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments

# Charger les données
data = load_dataset('csv', data_files={'train': ['fr.txt', 'la.txt']}, 
                    split='train', delimiter='\t')

# Charger le modèle et le tokenizer
model_name = "Helsinki-NLP/opus-mt-fr-la"  # Exemple pour le modèle de base français-latin
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def encode_data(examples):
    inputs = tokenizer(examples['source'], truncation=True, padding=True, max_length=128)
    targets = tokenizer(examples['target'], truncation=True, padding=True, max_length=128)
    inputs['labels'] = targets['input_ids']
    return inputs

encoded_data = data.map(encode_data, batched=True)


# Définir les arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True
)

# Créer l'entraîneur
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=encoded_data
)

# Lancer l'entraînement
trainer.train()

model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

inputs = tokenizer("Bonjour, comment allez-vous ?", return_tensors="pt", truncation=True)
outputs = model.generate(**inputs)
translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(translated)
