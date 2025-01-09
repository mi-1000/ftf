from typing import Literal
from .llm import LLM

llm = LLM()

lang_code_to_name = {
    "fr": "French",
    "fro": "Old French",
    "grc": "Ancient Greek",
    "la": "Latin",
}

lang_name_to_code = {value: key for key, value in lang_code_to_name.items()}

BOILERPLATE_PROMPT = """Translate the following text from {source_lang} to {target_lang}. Reply with the translation only, without explanations or additional text:
"{text}"
"""

BOILERPLATE_CONTEXT = """
You are an expert in ancient European languages, including Old French from the medieval period, Ancient Greek and Latin, as well as Standard Modern French.
Translate the provided text into {target_lang}. Maintain historical and linguistical accuracy. Reply with the translation only and nothing else.
"""

async def translate(source_lang: Literal['fr', 'fro', 'grc', 'la'], target_lang: Literal['fr', 'fro', 'grc', 'la'], text: str) -> str:
    allowed_languages = ['fr', 'fro', 'grc', 'la']
    if source_lang not in allowed_languages or target_lang not in allowed_languages:
        raise ValueError("Incorrect language code provided in parameters of translate(source_lang, target_lang, text). Authorized values are 'fr', 'fro', 'grc', 'la'.")
    source = lang_code_to_name[source_lang]
    target = lang_code_to_name[target_lang]
    prompt = BOILERPLATE_PROMPT.format(source_lang=source, target_lang=target, text=text)
    context = BOILERPLATE_CONTEXT.format(target_lang=target_lang)
    res = await llm.prompt(prompt, context)
    return res