import re
import unicodedata

from typing import Literal

TILDE = "\u0303"
csourde = r"[ptkfsçx]"
double_consonne = r"(nn|mm)"
zsv = r"[zsv]"
voyelle_api_pas_latine = r"[ɑəɛ]"
voyelle_sans_crochets = "aeiouyæœéèêëàâùûüïîÿ"
consonne_sans_crochets = "bcçdfghjklmnpqrstvwxz"
voyelle = rf"[{voyelle_sans_crochets}]"
consonne = rf"[{consonne_sans_crochets}]"
lettre = rf"[{voyelle_sans_crochets}{consonne_sans_crochets}]"

data = {
    # Cas particuliers
    r"aim\b": {"ear": "ɛ̃m", "lat": "ɛ̃m"},
    r"oian\b": {"ear": "weJãn", "lat": "weJã"}, # J majuscule pour l'instant pour ne pas mélanger l'API et les caractères latins
    r"oien\b": {"ear": "weJãn", "lat": "weJã"},
    r"aign": {"ear": "aJɳ", "lat": "aɳ"},
    r"eign": {"ear": "ɛJɳ", "lat": "ɛɳ"},
    r"ign\b": {"ear": "ɳ", "lat": "ɳ"},
    r"ing\b": {"ear": "ŋ", "lat": "ŋ"},
    r"oie": {"ear": "oi", "lat": "oi"}, # Sera transformé plus tard
    
    # Di- et triphtongues
    r"eau": {"ear": "iao", "lat": "Eao"}, # Pareil pour e
    r"ieu": {"ear": "Jeu", "lat": "Jeu"},
    r"uou": {"ear": "uou", "lat": "u̯ou"},
    r"oi": {"ear": "ɔJ", "lat": "wɛ"},
    r"ei": {"ear": "ɛJ", "lat": "ɛ"},
    r"au": {"ear": "ao", "lat": "ao"},
    r"eu": {"ear": "ø", "lat": "Jœ"},
    r"ie": {"ear": "Jɛ", "lat": "Jɛ"},
    r"ue": {"ear": "uE", "lat": "œ"},
    r"ou": {"ear": "u", "lat": "u"},
    r"oe": {"ear": "wɛ", "lat": "œ"},
    
    # Groupes
    r"sch": {"ear": "ʃ", "lat": "ʃ"},
    r"ch": {"ear": "tʃ", "lat": "ʃ"},
    r"ge": {"ear": "d͡ʒE", "lat": "d͡ʒE"},
    r"gi": {"ear": "d͡ʒi", "lat": "d͡ʒi"},
    r"ll": {"ear": "J", "lat": "J"},
    r"ph": {"ear": "f", "lat": "f"},
    r"qu?": {"ear": "k", "lat": "k"},
    
    r"os": {
        "ear": "os",
        "lat": "oː",  # O long
    },
    r"or": {
        "ear": "ɔr",
        "lat": "ɔr",
    },
    rf"ol({consonne}|\b)": {
        "ear": r"ɔl\1",
        "lat": r"u\1",
    },
    rf"ol({voyelle})": {
        "ear": r"ɔl\1",
        "lat": r"ɔl\1",
    },
    
    r"an": {"ear": "ɑ̃n", "lat": "ɑ̃"},
    r"en": {"ear": "ɑ̃n", "lat": "ɑ̃"},
    r"on": {"ear": "õn", "lat": "õ"},
    r"in": {"ear": "ɛ̃n", "lat": "ɛ̃"},
    r"un": {"ear": "œ̃n", "lat": "œ̃"},
    r"oin": {"ear": "wɛ̃n", "lat": "wɛ̃"},

    # Diphthongues
    rf"({lettre})ai({lettre})": {
        "ear": r"\1aJ\2",
        "lat": r"\1ɛ\2",
    },
    r"ai": {"ear": "EJ", "lat": "E"},
    
    # Consonnes finales
    r"t\b": {  # -t final
        "ear": "θ",  # jusqu'au XIè siècle
        "lat": "t",
    },
    r"z\b": {  # -z final
    "ear": "t͡s",
    "lat": "s",
    },
    rf"({voyelle}{TILDE}?)z\b": {  # Vérifie si une voyelle nasalisée précède le "z" final
    "ear": r"\1t͡s",  # Conserve la nasalisation en phonétique
    "lat": r"\1s",    # Conserve la nasalisation en latin
    },
    r"s\b": {  # -s final
        "ear": "s",  # jusqu'au XIIIè siècle
        "lat": "",  # Non prononcé
    },
    r"x\b": {
        "ear": "ɥs",
        "lat": "ɥs",
    },
    
    r"c([e|i|y])": {"ear": r"t͡s\1", "lat": r"t͡s\1"},
    r"\bh": {"ear": "", "lat": ""},

    # Consonnes simples et groupes
    r"c": {"ear": "k", "lat": "k"},
    r"ç": {"ear": "s", "lat": "s"},
    r"s": {"ear": "s", "lat": "s"},
    r"g": {"ear": "g", "lat": "g"},
    r"k": {"ear": "k", "lat": "k"},
    r"j": {"ear": "d͡ʒ", "lat": "d͡ʒ"},
    r"y": {"ear": "j", "lat": "j"},
    r"m": {"ear": "m", "lat": "m"},
    r"n": {"ear": "n", "lat": "n"},
    r"r": {"ear": "r", "lat": "r"},  # R roulé
    r"f": {"ear": "f", "lat": "f"},
    r"v": {"ear": "v", "lat": "v"},
    r"p": {"ear": "p", "lat": "p"},
    r"b": {"ear": "b", "lat": "b"},
    
    r"J": {"ear": "j", "lat": "j"}, # Maintenant qu'on a converti la lettre j on remet l'API

    # Voyelles simples et nasales
    r"i": {"ear": "i", "lat": "i"},
    r"y": {"ear": "i", "lat": "i"},
    r"ÿ": {"ear": "i", "lat": "i"},
    r"ï": {"ear": "j", "lat": "j"},
    r"î": {"ear": "iː", "lat": "iː"},
    r"â": {"ear": "ɑː", "lat": "ɑː"},
    r"à": {"ear": "a", "lat": "a"},
    r"ü": {"ear": "y", "lat": "y"},
    r"û": {"ear": "uː", "lat": "uː"},
    r"ù": {"ear": "u", "lat": "u"},
    r"u": {"ear": "u", "lat": "u"},
    r"e": {"ear": "ə", "lat": "ə"},
    r"ë": {"ear": "ə", "lat": "ə"},
    r"é": {"ear": "e", "lat": "e"},
    r"è": {"ear": "ɛ", "lat": "ɛ"},
    r"ê": {"ear": "ɛː", "lat": "ɛː"},
    r"a": {"ear": "a", "lat": "a"},
    rf"o({zsv})": { # pareil qu'après sauf devant z, s, v
        "ear": r"oː\1", # "chose"
        "lat": r"oː\1",
    },
    rf"o({double_consonne})": {  # ò ouvert suivi de 2 consonnes
        "ear": r"ɔ\1",  # "bonne"
        "lat": r"ɔ\1",
    },
    r"o": {"ear": "o", "lat": "u"},  # Atone libre / tonique entravé
    
    r"E": {"ear": "e", "lat": "e"}, # On rechange le e
    
    rf"y(m|n)": {"ear": r"i\1", "lat": r"i\1"},
    
    rf"({voyelle}|{voyelle_api_pas_latine})(ː?)m({consonne})": {  # Nasalisation par "m"
        "ear": rf"\1{TILDE}\2m\3",
        "lat": rf"\1{TILDE}\2\3",
    },
    rf"({voyelle}|{voyelle_api_pas_latine})(ː?)n({consonne})": {  # Nasalisation par "n"
        "ear": rf"\1{TILDE}\2n\3",
        "lat": rf"\1{TILDE}\2\3",
    },
    rf"({voyelle}|{voyelle_api_pas_latine})(ː?)m({voyelle})": {  # Nasalisation par "m"
        "ear": rf"\1{TILDE}\2m\3",
        "lat": rf"\1{TILDE}m\2\3",
    },
    rf"({voyelle}|{voyelle_api_pas_latine})(ː?)n({voyelle})": {  # Nasalisation par "n"
        "ear": rf"\1{TILDE}\2n\3",
        "lat": rf"\1{TILDE}n\2\3",
    },
}

def clean(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text) # Remplacement des sauts de ligne, tabulations etc. par un espace simple
    text = re.sub(rf"[^{voyelle_sans_crochets}{consonne_sans_crochets}\s]", "", text) # Suppression des caractères non autorisés
    text = re.sub(r"\s+", " ", text) # Remplacement des multiples espaces nouvellement créés
    text = text.strip()
    return text

def phoneticize(text: str, period: Literal['ear', 'lat'] = "ear") -> str:
    if period not in ['ear', 'lat']:
        raise ValueError("Period must be [ear]ly or [lat]e Old French.")
    text = clean(text)
    for regex, rule in data.items():
        text = re.sub(regex, rule[period], text)
    return unicodedata.normalize("NFKC", text)