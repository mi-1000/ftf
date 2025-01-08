from typing import Literal
from llm import LLM

llm = LLM()

lang_code_to_name = {
    "fr": "French",
    "fro": "Old French",
    "grc": "Ancient Greek",
    "la": "Latin",
}

lang_name_to_code = {value: key for key, value in lang_code_to_name.items()}

BOILERPLATE_PROMPT = """
Translate and reply only with the translation of the following text from {source_lang} to {target_lang}:
"{text}"
"""

BOILERPLATE_CONTEXT = """
You are an expert in ancient European languages, including Old French from the medieval period, Ancient Greek and Latin, as well as Standard Modern French.
Translate the provided text into {target_lang}, being as close as possible to the original text in terms of meaning and structure, and reply with the translation only and nothing else.
"""
# Here are some translation examples:
# - "{t1}" -> "{t2}"
# - "{t3}" -> "{t4}"
# - "{t5}" -> "{t6}"
# - "{t7}" -> "{t8}"
# """

# def get_x_to_french_examples(lang: Literal['fro', 'grc', 'la']):
#     match lang:
#         case "fro":
#             return {
#                 "fr": [
#                     "Écoutez, seigneurs, quel péché nous accable. L'empereur Charles de douce France est venu dans ce pays pour nous confondre. Je n'ai pas d'armée pour lui donner bataille, ni de gens pour briser la sienne.",
#                     "Envoyons-y les fils de nos épouses",
#                     "L'empereur garde la tête inclinée. Il n'est pas prompt à parler, sa coutume est de parler à loisir.",
#                     "Les cottes de mailles et les casques jettent un grand éclat",
#                 ],
#                 "fro": [
#                     "Oez, seignurs, quel pecchet nus encumbret. Li empereres Carles de France dulce en cest païs nos est venuz cunfundre. Jo nen ai ost qui bataille li dunne, ne n'ai tel gent ki la sue derumpet.",
#                     "Enveiuns i les filz de noz muillers",
#                     "Li empereres en tint sun chef enclin. De sa parole ne fut mie hastifs, sa custume est qu'il parolet a leisir.",
#                     "Osbercs e helmes i getent grant flabur",
#                 ],
#             }
#         case "grc":
#             return {
#                 "fr": [
#                     "Que médites-tu ? Quelle est ta pensée ?",
#                     "Il n'a nul droit de me repousser loin des miens.",
#                     "À cette vue, le divin Ulysse s'arrête étonné.",
#                     "Étranger, venez dormir, votre lit est prêt.",
#                 ],
#                 "grc": [
#                     "ποῖόν τι κινδύνευμα; ποῦ γνώμης ποτ᾽ εἰ;",
#                     "ἀλλ᾽ οὐδὲν αὐτῷ τῶν ἐμῶν μ᾽ εἴργειν μέτα.",
#                     "Ἔνθα στὰς θηεῖτο πολύτλας δῖος Ὀδυσσεύς.",
#                     "Ὄρσο κέων, ὦ ξεῖνε· πεποίηται δέ τοι εὐνή.",
#                 ],
#             }
#         case "la":
#             return {
#                 "fr": [
#                     "Le jour où Elkana offrait son sacrifice, il donnait des portions à Peninna, sa femme, et à tous les fils et à toutes les filles qu'il avait d'elle.",
#                     "Tu te conformeras à la loi qu'ils t'enseigneront et à la sentence qu'ils auront prononcée ; tu ne te détourneras de ce qu'ils te diront ni à droite ni à gauche.",
#                     "On dirait, en vérité, que le genre humain c'est vous, et qu'avec vous doit mourir la sagesse.",
#                     "Parle à la terre, elle t'instruira ; et les poissons de la mer te le raconteront.",
#                 ],
#                 "la": [
#                     "venit ergo dies et immolavit Helcana deditque Fenennae uxori suae et cunctis filiis eius et filiabus partes",
#                     "iuxta legem eius sequeris sententiam eorum nec declinabis ad dextram vel ad sinistram",
#                     "ergo vos estis soli homines et vobiscum morietur sapientia",
#                     "loquere terrae et respondebit tibi et narrabunt pisces maris",
#                 ],
#             }
#         case _: # Should not happen
#             return ValueError("Parameter must be either 'fro', 'grc' or 'la'.")

# def get_translation_examples(source_lang: Literal['fr', 'fro', 'grc', 'la'], target_lang: Literal['fr', 'fro', 'grc', 'la']):
#     if source_lang == target_lang:
#         raise ValueError("Source and target language should be different.")
    
#     output_examples = []
    
#     if source_lang == "fr":
#         examples = get_x_to_french_examples() # TODO
        
    
#     return {
#         "t1": examples[0],
#         "t2": examples[1],
#         "t3": examples[2],
#         "t4": examples[3],
#         "t5": examples[4],
#         "t6": examples[5],
#         "t7": examples[6],
#         "t8": examples[7],
#     }

def translate(source_lang: Literal['fr', 'fro', 'grc', 'la'], target_lang: Literal['fr', 'fro', 'grc', 'la'], text):
    allowed_languages = ['fr', 'fro', 'grc', 'la']
    if source_lang not in allowed_languages or target_lang not in allowed_languages:
        raise ValueError("Incorrect language code provided in parameters of translate(source_lang, target_lang, text). Authorized values are 'fr', 'fro', 'grc', 'la'.")
    source = lang_code_to_name[source_lang]
    target = lang_code_to_name[target_lang]
    # examples = get_translation_examples(source_lang, target_lang)
    prompt = BOILERPLATE_PROMPT.format(source_lang=source, target_lang=target, text=text)
    context = BOILERPLATE_CONTEXT.format(target_lang=target_lang) #, **examples)
    res = llm.prompt(prompt, context)
    return res

if __name__ == "__main__":
    print(translate("grc", "fro", "Καὶ σὺ τέκνον!"))