import re
import unicodedata

from typing import Literal

TILDE = "\u0303"
voiceless_consonant = r"[ptkfsçx]"
double_consonant = r"(nn|mm)"
zsv = r"[zsv]"
non_latin_ipa_vowel = r"[ɑəɛ]"
vowel_no_brackets = "aeiouyæœéèêëàâùûüïîÿ"
consonant_no_brackets = "bcçdfghjklmnpqrstvwxz"
vowel = rf"[{vowel_no_brackets}]"
consonant = rf"[{consonant_no_brackets}]"
letter = rf"[{vowel_no_brackets}{consonant_no_brackets}]"

data = {
    # Particular cases
    r"aim\b": {"ear": "ɛ̃m", "lat": "ɛ̃m"},
    r"oian\b": {"ear": "wEJãn", "lat": "wEJã"}, # Uppercase E/J for now, so as to not mix up between IPA and latin chars, will change back later
    r"oien\b": {"ear": "wEJɛ̃n", "lat": "wEJɛ̃"},
    r"aign": {"ear": "aJɳ", "lat": "aɳ"},
    r"eign": {"ear": "ɛJɳ", "lat": "ɛɳ"},
    r"ign\b": {"ear": "ɳ", "lat": "ɳ"},
    r"ing\b": {"ear": "iŋ", "lat": "iŋ"},
    r"oie": {"ear": "oi", "lat": "oi"}, # Will be changed later
    
    # Di- and triphtongs
    r"eau": {"ear": "iao", "lat": "Eao"}, # Same
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
    
    # Groups
    r"sch": {"ear": "ʃ", "lat": "ʃ"},
    r"ch": {"ear": "tʃ", "lat": "ʃ"},
    r"ge": {"ear": "d͡ʒE", "lat": "d͡ʒE"},
    r"gi": {"ear": "d͡ʒi", "lat": "d͡ʒi"},
    r"ll": {"ear": "J", "lat": "J"},
    r"ph": {"ear": "f", "lat": "f"},
    r"qu?": {"ear": "k", "lat": "k"},
    
    r"os": {
        "ear": "os",
        "lat": "oː",  # Long O
    },
    r"or": {
        "ear": "ɔr",
        "lat": "ɔr",
    },
    rf"ol({consonant}|\b)": {
        "ear": r"ɔl\1",
        "lat": r"u\1",
    },
    rf"ol({vowel})": {
        "ear": r"ɔl\1",
        "lat": r"ɔl\1",
    },
    
    r"an": {"ear": "ɑ̃n", "lat": "ɑ̃"},
    r"en": {"ear": "ɑ̃n", "lat": "ɑ̃"},
    r"on": {"ear": "õn", "lat": "õ"},
    r"in": {"ear": "ɛ̃n", "lat": "ɛ̃"},
    r"un": {"ear": "œ̃n", "lat": "œ̃"},
    r"oin": {"ear": "wɛ̃n", "lat": "wɛ̃"},

    # Diphthongs
    rf"({letter})ai({letter})": {
        "ear": r"\1aJ\2",
        "lat": r"\1ɛ\2",
    },
    r"ai": {"ear": "EJ", "lat": "E"},
    
    # Final consonants
    r"t\b": {  # Final -t 
        "ear": "θ",  # Until XIth century
        "lat": "t",
    },
    r"z\b": {  # Final -z 
    "ear": "t͡s",
    "lat": "s",
    },
    rf"({vowel}{TILDE}?)z\b": {  # Check if nasalized vowel precedes final -z
    "ear": r"\1t͡s",
    "lat": r"\1s",
    },
    r"s\b": {  # Final -s
        "ear": "s",  # Until XIIIth century
        "lat": "",  # Not pronounced
    },
    r"x\b": {
        "ear": "ɥs",
        "lat": "ɥs",
    },
    
    r"c([e|i|y])": {"ear": r"t͡s\1", "lat": r"t͡s\1"},
    r"\bh": {"ear": "", "lat": ""},

    # Simple consonants and groups
    r"c": {"ear": "k", "lat": "k"},
    r"ç": {"ear": "s", "lat": "s"},
    r"s": {"ear": "s", "lat": "s"},
    r"g": {"ear": "g", "lat": "g"},
    r"k": {"ear": "k", "lat": "k"},
    r"j": {"ear": "d͡ʒ", "lat": "d͡ʒ"},
    r"y": {"ear": "j", "lat": "j"},
    r"m": {"ear": "m", "lat": "m"},
    r"n": {"ear": "n", "lat": "n"},
    r"r": {"ear": "r", "lat": "r"},  # Rolled R
    r"f": {"ear": "f", "lat": "f"},
    r"v": {"ear": "v", "lat": "v"},
    r"p": {"ear": "p", "lat": "p"},
    r"b": {"ear": "b", "lat": "b"},
    
    r"J": {"ear": "j", "lat": "j"}, # Now we converted letter j we revert IPA

    # Simple vowels and nasals
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
    rf"o({zsv})": { # Same as under except before z, s, v
        "ear": r"oː\1", # "chose"
        "lat": r"oː\1",
    },
    rf"o({double_consonant})": {  # Open ò followed by 2 consonants
        "ear": r"ɔ\1",  # "bonne"
        "lat": r"ɔ\1",
    },
    r"o": {"ear": "o", "lat": "u"},
    
    r"E": {"ear": "e", "lat": "e"}, # Changing back e
    
    rf"y(m|n)": {"ear": r"i\1", "lat": r"i\1"},
    
    rf"({vowel}|{non_latin_ipa_vowel})(ː?)m({consonant})": {  # Nasalization through "m"
        "ear": rf"\1{TILDE}\2m\3",
        "lat": rf"\1{TILDE}\2\3",
    },
    rf"({vowel}|{non_latin_ipa_vowel})(ː?)n({consonant})": {  # Nasalization through "n"
        "ear": rf"\1{TILDE}\2n\3",
        "lat": rf"\1{TILDE}\2\3",
    },
    rf"({vowel}|{non_latin_ipa_vowel})(ː?)m({vowel})": {
        "ear": rf"\1{TILDE}\2m\3",
        "lat": rf"\1{TILDE}m\2\3",
    },
    rf"({vowel}|{non_latin_ipa_vowel})(ː?)n({vowel})": {
        "ear": rf"\1{TILDE}\2n\3",
        "lat": rf"\1{TILDE}n\2\3",
    },
}

def clean(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text) # Replacing line feeds, tabs etc. by a simple space
    text = re.sub(rf"[^{vowel_no_brackets}{consonant_no_brackets}\s]", "", text) # Remove unauthorized chars
    text = re.sub(r"\s+", " ", text) # Replacing multiple spaces newly created by a single one again
    text = text.strip()
    return text

def phoneticize(text: str, period: Literal['ear', 'lat'] = "ear") -> str:
    if period not in ['ear', 'lat']:
        raise ValueError("Period must be [ear]ly or [lat]e Old French.")
    text = clean(text)
    for regex, rule in data.items():
        text = re.sub(regex, rule[period], text)
    return unicodedata.normalize("NFKC", text)