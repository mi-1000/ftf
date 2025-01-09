import logging
import os
import torch

from dotenv import load_dotenv, find_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

load_dotenv(find_dotenv())

base_model = os.getenv("LLAMA_MODEL_PATH")

tokenizer = AutoTokenizer.from_pretrained(base_model)

if not torch.cuda.is_available():
    logging.warning("CUDA is not available.")

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)

if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id
if model.config.pad_token_id is None:
    model.config.pad_token_id = model.config.eos_token_id

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.float16,
    device_map="auto",
)

if __name__ == "__main__": # Test out model first
    messages = [{"role": "user", "content": "Who is Vincent van Gogh?"}]

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    outputs = pipe(prompt, max_new_tokens=120, do_sample=True)

    print(outputs[0]["generated_text"])