# [NOTE] Implementation and free adaptation of the following Lua modules from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:grc-utilities/data
# https://en.wiktionary.org/wiki/Module:grc-pronunciation/data
# Last revision: 2024-12-23

from functools import lru_cache

PERIODS = ['cla', 'koi1', 'koi2', 'byz1', 'byz2']

TIE = "\u035C"  # tie bar — ͜
NONSYLLABIC = "\u032F"  # combining inverted breve below — ̯
HIGH = "\u0341"  # combining acute tone mark — ́
LOW = "\u0340"  # combining grave tone mark — ̀
RISING = "\u030C"  # combining caron — ̌
FALLING = "\u0302"  # combining circumflex — ̂
MID_HIGH = "\u1DC4"  # mid–high pitch — ᷄
MID_LOW = "\u1DC6"  # mid–low pitch — ᷆
HIGH_MID = "\u1DC7"  # high–mid pitch — ᷇
VOICELESS = "\u0325"  # combining ring below — ̥
ASPIRATED = "\u02B0"  # superscript h — ʰ
MACRON = "\u0304"  # macron — ¯
BREVE = "\u0306"  # breve — ˘

# ---- Some of these constants overlap -- this is for compatibility with the original Lua code

COMBINING_MACRON = "\u0304"  # macron - ̄
SPACING_MACRON = "\u00AF"  # spacing macron - ¯
MODIFIER_MACRON = "\u02C9"  # modifier macron - ˉ
COMBINING_BREVE = "\u0306"  # breve - ̆
SPACING_BREVE = "\u02D8"  # spacing breve - ˘
ROUGH = "\u0314"  # rough - ̔
SMOOTH = "\u0313"  # smooth - ̓
DIAERESIS = "\u0308"  # diaeresis - ̈
ACUTE = "\u0301"  # acute - ́
GRAVE = "\u0300"  # grave - ̀
CIRCUM = "\u0342"  # circum - ͂
LATIN_CIRCUM = "\u0302"  # Latin circumflex - ̂
CORONIS = "\u0343"  # coronis - ̓
SUBSCRIPT = "\u0345"  # subscript - ͅ
UNDERTIE = "\u035C"  # undertie - ͜

CHAR_SETS = {
    "cons": "bɡŋdzklmnprstβðɣɸθxfvɟʝcçwʍj",
    "vowel": "aeiouyɛɔ",
    "diacritic": HIGH
        + LOW
        + MID_HIGH
        + MID_LOW
        + HIGH_MID
        + LATIN_CIRCUM
        + ASPIRATED
        + VOICELESS
        + NONSYLLABIC
        + RISING
        + FALLING,
    "liquid": "rln",
    "obst": "bɡdkptβðɣɸθxfv",
    "frontDiphth": "[αο]ι",
    "frontVowel": "ιηευ",
    "iDiaer": "ϊΐῒῗ",
    "long": "ηω",
    "short": "εο",
    "ambig": "αιυ",
    "uDiphth": "αεηο",
    "iDiphth": "αεου",
    "Greekdiacritic": COMBINING_MACRON
        + SPACING_MACRON
        + MODIFIER_MACRON
        + COMBINING_BREVE
        + SPACING_BREVE
        + ROUGH
        + SMOOTH
        + DIAERESIS
        + ACUTE
        + GRAVE
        + CIRCUM
        + LATIN_CIRCUM
        + CORONIS
        + SUBSCRIPT
        + UNDERTIE,
    "Greekconsonant": "ΒβΓγΔδΖζΘθΚκΛλΜμΝνΞξΠπΡρΣσςΤτΦφΧχΨψ",
}

ALL_DIACRITICS = [
    COMBINING_MACRON,
    SPACING_MACRON,
    MODIFIER_MACRON,
    COMBINING_BREVE,
    SPACING_BREVE,
    ROUGH,
    SMOOTH,
    DIAERESIS,
    ACUTE,
    GRAVE,
    CIRCUM,
    LATIN_CIRCUM,
    CORONIS,
    SUBSCRIPT,
    UNDERTIE,
]

UNACCENTED_GREEK_LETTERS = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"

data_wrapper = (
    {
        " ": {
            "p": {
                "cla": " ",
                "koi1": " ",
                "koi2": " ",
                "byz1": " ",
                "byz2": " ",
            },
        },
        "β": {
            "clusters": {
                "δ": True,
                "λ": True,
                "ρ": True,
            },
            "p": {
                "cla": "b",
                "koi1": "b",
                "koi2": (
                    ("-1=μ", "b"),
                    "β",
                ),
                "byz1": (
                    ("-1=μ", "b"),
                    "v",
                ),
                "byz2": (
                    ("1=β", ""),
                    ("-1=μ", "b"),
                    "v",
                ),
            },
        },
        "γ": {
            "clusters": {
                "λ": True,
                "ν": True,
                "ρ": True,
            },
            "p": {
                "cla": (
                    ("1.dorsal/1=μ", "ŋ"),
                    "ɡ",
                ),
                "koi1": (
                    ("1.dorsal", "ŋ"),
                    "ɡ",
                ),
                "koi2": (
                    ("1.dorsal", (("1~preFront", "ɲ"), "ŋ")),
                    ("0~preFront", (("-1=γ", "ɟ"), "ʝ")),
                    ("-1=γ", "ɡ"),
                    "ɣ",
                ),
                "byz1": (
                    ("1.dorsal", (("1~preFront", "ɲ"), "ŋ")),
                    ("0~preFront", (("-1=γ", "ɟ"), "ʝ")),
                    ("-1=γ", "ɡ"),
                    "ɣ",
                ),
                "byz2": (
                    ("1.dorsal", (("1~preFront", "ɲ"), "ŋ")),
                    ("0~preFront", (("-1=γ", "ɟ"), "ʝ")),
                    ("-1=γ", "ɡ"),
                    "ɣ",
                ),
            },
        },
        "δ": {
            "clusters": {
                "ρ": True,
            },
            "p": {
                "cla": "d",
                "koi1": "d",
                "koi2": (
                    ("-1=ν", "d"),
                    "ð",
                ),
                "byz1": (
                    ("-1=ν", "d"),
                    "ð",
                ),
                "byz2": (
                    ("1=δ", ""),
                    ("-1=ν", "d"),
                    "ð",
                ),
            },
        },
        "ζ": {
            "clusters": {},
            "p": {
                "cla": "zd",
                "koi1": "z",
                "koi2": "z",
                "byz1": "z",
                "byz2": (
                    ("1=ζ", ""),
                    "z",
                ),
            },
        },
        "θ": {
            "clusters": {
                "ρ": True,
            },
            "p": {
                "cla": "tʰ",
                "koi1": "tʰ",
                "koi2": "θ",
                "byz1": "θ",
                "byz2": (
                    ("1=θ", ""),
                    "θ",
                ),
            },
        },
        "κ": {
            "clusters": {
                "λ": True,
                "ν": True,
                "τ": True,
                "ρ": True,
            },
            "p": {
                "cla": (
                    ("1.voiced+1.stop", "ɡ"),
                    ("1.aspirated", "kʰ"),
                    "k",
                ),
                "koi1": (
                    ("1.voiced+1.stop", "ɡ"),
                    "k",
                ),
                "koi2": (
                    ("1=κ", ""),
                    ("1.voiced+1.stop", "ɡ"),
                    ("-1=γ", (("0~preFront", "ɟ"), "ɡ")),
                    ("0~preFront", "c"),
                    "k",
                ),
                "byz1": (
                    ("1=κ", ""),
                    ("1.voiced+1.stop", "ɡ"),
                    ("-1=γ", (("0~preFront", "ɟ"), "ɡ")),
                    ("0~preFront", "c"),
                    "k",
                ),
                "byz2": (
                    ("1=κ", ""),
                    ("1.voiced+1.stop", "ɡ"),
                    ("-1=γ", (("0~preFront", "ɟ"), "ɡ")),
                    ("0~preFront", "c"),
                    "k",
                ),
            },
        },
        "λ": {
            "clusters": {},
            "p": {
                "cla": "l",
                "koi1": "l",
                "koi2": "l",
                "byz1": "l",
                "byz2": (
                    ("1=λ", ""),
                    "l",
                ),
            },
        },
        "μ": {
            "clusters": {
                "ν": True,
            },
            "p": {
                "cla": "m",
                "koi1": "m",
                "koi2": "m",
                "byz1": "m",
                "byz2": (
                    ("1=μ", ""),
                    "m",
                ),
            },
        },
        "ν": {
            "clusters": {},
            "p": {
                "cla": "n",
                "koi1": "n",
                "koi2": "n",
                "byz1": "n",
                "byz2": (
                    ("1=ν", ""),
                    "n",
                ),
            },
        },
        "ξ": {
            "clusters": {},
            "p": {
                "cla": "ks",
                "koi1": "ks",
                "koi2": "ks",
                "byz1": "ks",
                "byz2": "ks",
            },
        },
        "π": {
            "clusters": {
                "λ": True,
                "ν": True,
                "ρ": True,
                "τ": True,
            },
            "p": {
                "cla": (
                    ("1.aspirated", "pʰ"),
                    "p",
                ),
                "koi1": "p",
                "koi2": "p",
                "byz1": "p",
                "byz2": (
                    ("-1=μ", "b"),
                    ("1=π", ""),
                    "p",
                ),
            },
        },
        "ρ": {
            "clusters": {},
            "p": {
                "cla": (
                    ("1=ρ/1=ῥ/-1=ρ", "r̥"),
                    "r",
                ),
                "koi1": "r",
                "koi2": "r",
                "byz1": "r",
                "byz2": (
                    ("1=ρ", ""),
                    "r",
                ),
            },
        },
        "ῥ": {
            "clusters": {},
            "p": {
                "cla": "r̥",
                "koi1": "r",
                "koi2": "r",
                "byz1": "r",
                "byz2": (
                    ("1=ρ", ""),
                    "r",
                ),
            },
        },
        "σ": {
            "clusters": {
                "β": True,
                "θ": True,
                "κ": True,
                "μ": True,
                "π": True,
                "τ": True,
                "φ": True,
                "χ": True,
            },
            "p": {
                "cla": (
                    ("1.voiced", "z"),
                    "s",
                ),
                "koi1": (
                    ("1.voiced", "z"),
                    "s",
                ),
                "koi2": (
                    ("1.voiced", "z"),
                    "s",
                ),
                "byz1": (
                    ("1.voiced", "z"),
                    "s",
                ),
                "byz2": (
                    ("1=σ", ""),
                    ("1.voiced", "z"),
                    "s",
                ),
            },
        },
        "τ": {
            "clusters": {
                "λ": True,
                "μ": True,
                "ρ": True,
            },
            "p": {
                "cla": (
                    ("1.aspirated", "tʰ"),
                    "t",
                ),
                "koi1": "t",
                "koi2": "t",
                "byz1": "t",
                "byz2": (
                    ("-1=ν", "d"),
                    ("1=τ", ""),
                    "t",
                ),
            },
        },
        "φ": {
            "clusters": {
                "θ": True,
                "λ": True,
                "ρ": True,
            },
            "p": {
                "cla": "pʰ",
                "koi1": "pʰ",
                "koi2": "ɸ",
                "byz1": "f",
                "byz2": (
                    ("1=φ", ""),
                    "f",
                ),
            },
        },
        "χ": {
            "clusters": {
                "θ": True,
                "λ": True,
                "ρ": True,
            },
            "p": {
                "cla": "kʰ",
                "koi1": "kʰ",
                "koi2": (
                    ("1=χ", ""),
                    ("0~preFront", "ç"),
                    "x",
                ),
                "byz1": (
                    ("1=χ", ""),
                    ("0~preFront", "ç"),
                    "x",
                ),
                "byz2": (
                    ("1=χ", ""),
                    ("0~preFront", "ç"),
                    "x",
                ),
            },
        },
        "ψ": {
            "clusters": {},
            "p": {
                "cla": "ps",
                "koi1": "ps",
                "koi2": "ps",
                "byz1": "ps",
                "byz2": "ps",
            },
        },
        "ϝ": {
            "clusters": {},
            "p": {
                "cla": "w",
                "koi1": "",
                "koi2": "",
                "byz1": "",
                "byz2": "",
            },
        },
        "α": {
            "pre": (
                ("0~isIDiphth/0~isUDiphth/0~hasMacronBreve", 1),
                0,
            ),
            "p": {
                "cla": "a",
                "koi1": "a",
                "koi2": "a",
                "byz1": "a",
                "byz2": "a",
            },
        },
        "ε": {
            "pre": (
                ("0~isIDiphth/0~isUDiphth", 1),
                0,
            ),
            "p": {
                "cla": "e",
                "koi1": "e",
                "koi2": "e",
                "byz1": "e",
                "byz2": "e",
            },
        },
        "η": {
            "pre": (
                ("0~isUDiphth", 1),
                0,
            ),
            "p": {
                "cla": "ɛ",
                "koi1": "e̝",
                "koi2": "i",
                "byz1": "i",
                "byz2": "i",
            },
        },
        "ι": {
            "p": {
                "cla": "i",
                "koi1": "i",
                "koi2": "i",
                "byz1": "i",
                "byz2": "i",
            },
        },
        "ο": {
            "pre": (
                ("0~isIDiphth/0~isUDiphth", 1),
                0,
            ),
            "p": {
                "cla": "o",
                "koi1": "o",
                "koi2": "o",
                "byz1": "o",
                "byz2": "o",
            },
        },
        "υ": {
            "pre": (
                ("0~isIDiphth/0~hasMacronBreve", 1),
                0,
            ),
            "p": {
                "cla": "y",
                "koi1": "y",
                "koi2": "y",
                "byz1": "y",
                "byz2": "i",
            },
        },
        "ω": {
            "p": {
                "cla": "ɔ",
                "koi1": "o",
                "koi2": "o",
                "byz1": "o",
                "byz2": "o",
            },
        },
    },
)

data = data_wrapper[0] # Ugly workaround to get the content of the dictionary without any type mismatch

categories = {
    0: {
        "stop": ["π", "τ", "κ", "β", "δ", "γ", "φ", "θ", "χ", "ψ", "ξ"],
        "dorsal": ["κ", "γ", "χ", "ξ"],
        "voiced": ["β", "δ", "γ", "ζ", "μ", "ν", "λ", "ρ", "ϝ"],
        "unvoiced": ["π", "ψ", "τ", "κ", "ξ", "φ", "θ", "χ", "σ", "ς"],
        "aspirated": ["φ", "θ", "χ"],
        "diaer": ["ϊ", "ϋ", "ΐ", "ΰ", "ῒ", "ῢ", "ῗ", "ῧ"],
        "subi": ["ᾳ", "ῃ", "ῳ", "ᾴ", "ῄ", "ῴ", "ᾲ", "ῂ", "ῲ", "ᾷ", "ῇ", "ῷ"],
    },
    "type": {
        "vowel": ["α", "ε", "η", "ι", "ο", "ω", "υ"],
        "consonant": ["β", "γ", "δ", "ζ", "θ", "κ", "λ", "μ", "ν", "ξ", "π", "ρ", "σ", "ς", "τ", "φ", "χ", "ψ"],
        "long": ["η", "ω", "ᾱ", "ῑ", "ῡ"],
        "short": ["ε", "ο", "ᾰ", "ῐ", "ῠ"],
        "either": ["α", "ι", "υ"],
        "diacritic": [MACRON, SPACING_MACRON, MODIFIER_MACRON, BREVE, SPACING_BREVE, ROUGH, SMOOTH, DIAERESIS, ACUTE, GRAVE, CIRCUM, LATIN_CIRCUM, CORONIS, SUBSCRIPT],
    },
    "accent": {
        "acute": ["ά", "έ", "ή", "ί", "ό", "ύ", "ώ"],
        "grave": ["ὰ", "ὲ", "ὴ", "ὶ", "ὸ", "ὺ", "ὼ"],
        "circum": ["ᾶ", "ῆ", "ῖ", "ῦ", "ῶ"],
    },
    "breath": {
        "rough": ["ἁ", "ἑ", "ἡ", "ἱ", "ὁ", "ὑ", "ὡ"],
        "smooth": ["ἀ", "ἐ", "ἠ", "ἰ", "ὀ", "ὐ", "ὠ"],
    },
}

# Update data with additional info
def update_data(data, categories):
    # Loop over categories
    for category_key, category_data in categories.items():
        for subcategory_key, letters in category_data.items():
            for letter in letters:
                # Add a key for letters not yet in data
                if letter not in data:
                    from str_utils import strip_accent # Import only here to avoid circular import at start (because str_utils uses data from this module)
                    if strip_accent(letter) in data:
                        data[letter] = data[strip_accent(letter)] # Copy data from the stripped version of the letter
                        # TODO Might want to fix this later, doesn't seem to be optimal to me
                    else:
                        data[letter] = {}

                # If key is a numeric, we add it as a boolean
                if isinstance(category_key, int):
                    data[letter][subcategory_key] = True
                # If key is a string, we associate the name of the category to the subcategory
                elif isinstance(category_key, str):
                    data[letter][category_key] = subcategory_key

@lru_cache(maxsize=1)
def get_data():
    update_data(data, categories)
    return data