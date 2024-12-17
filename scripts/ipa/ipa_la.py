# [NOTE] Implementation and free adaptation of the following Lua module from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:la-pronunc
# Last revision: 2024-12-17

import re
from functools import lru_cache
from typing import Literal, Tuple

BREVE = "\u0306" # ̆
TILDE = "\u0303" # ̃
LONG = "\u02d0" # ː
HALF_LONG = "\u02d1" # ˑ

letters_ipa = {
    "a": "a",
    "e": "e",
    "i": "i",
    "o": "o",
    "u": "u",
    "y": "y",
    "ā": "aː",
    "ē": "eː",
    "ī": "iː",
    "ō": "oː",
    "ū": "uː",
    "ȳ": "yː",
    "ae": "ae̯",
    "oe": "oe̯",
    "ei": "ei̯",
    "au": "au̯",
    "eu": "eu̯",
    "b": "b",
    "d": "d",
    "f": "f",
    "c": "k",
    "g": "ɡ",
    "v": "w",
    "x": "ks",
    "ph": "pʰ",
    "th": "tʰ",
    "ch": "kʰ",
    "rh": "r",
    "qv": "kʷ",
    "gv": "ɡʷ",
    "'": "ˈ",
    "ˈ": "ˈ",
}

letters_ipa_eccl = {
    "a": "a",
    "e": "e",
    "i": "i",
    "o": "o",
    "u": "u",
    "y": "i",
    "ā": "aː",
    "ē": "eː",
    "ī": "iː",
    "ō": "oː",
    "ū": "uː",
    "ȳ": "iː",
    "ae": "eː",
    "oe": "eː",
    "ei": "ei̯",
    "au": "au̯",
    "eu": "eu̯",
    "b": "b",
    "d": "d",
    "f": "f",
    "k": "q",  # dirty hack to make sure k isn't palatalized
    "c": "k",
    "g": "ɡ",
    "v": "v",
    "x": "ks",
    "ph": "f",
    "th": "tʰ",
    "ch": "kʰ",
    "rh": "r",
    "qv": "kw",
    "gv": "ɡw",
    "sv": "sw",  # "sw" avoids [zv] in suavium
    "h": "",
    "'": "ˈ",
    "ˈ": "ˈ",
}

lax_vowel = {
    "e": "ɛ",
    "i": "ɪ",
    "o": "ɔ",
    "u": "ʊ",
    "y": "ʏ",
}

tense_vowel = {
    "ɛ": "e",
    "ɪ": "i",
    "ɔ": "o",
    "ʊ": "u",
    "ʏ": "y",
}

voicing = {
    "p": "b",
    "t": "d",
    "k": "ɡ",
}

devoicing = {
    "b": "p",
    "d": "t",
    "ɡ": "k",
}

classical_vowel_letters = "aeɛiɪoɔuʊyʏ"

classical_vowel = f"[{re.escape(classical_vowel_letters)}]"

phonetic_rules = [
    # Assimilation of [g] to [ŋ] before a following /n/.
    (r"ɡ([.ˈ]?)n", r"ŋ\1n"),
    # Per Allen (1978: 23), although note the reservations expressed on the next page.
    # Assimilation of word-internal /n/ and /m/ to following consonants.
    # Exception: /m/ does not assimilate to a following /n/.
    (r"n([.ˈ]?)([mpb])", r"m\1\2"),
    (r"n([.ˈ]?)([kɡ])", r"ŋ\1\2"),
    (r"m([.ˈ]?)([td])", r"n\1\2"),
    (r"m([.ˈ]?)([kɡ])", r"ŋ\1\2"),
    # Per George M. Lane: “Nasals changed their place of articulation to that of the following consonant.
    # Thus, dental n before the labials p and b became the labial m...
    # labial m before the gutturals c and g became guttural n...
    # labial m before the dentals t, d, s became dental n…” (§164.3);
    # “One nasal, n, is assimilated to another, m...but an m before n is never assimilated..." (§166.5).
    # Per Lloyd (1987: 84): “The opposition between nasals was neutralized in syllable-final position,
    # with the realization of the nasality being assimilated to the point of articulation of the following consonant,
    # e.g., [m] is found only before labials, [n] only before dentals or alveolars, and [ŋ] only before velars and /n/."
    # Potential addition: assimilation of final /m/ and /n/ across word boundaries, per e.g. Allen (1987: 28, 31).
    # No additional labialization before high back vowels
    (r"ʷ(?=uʊ)", ""),
    # Tensing of short vowels before another vowel
    (
        r"([ɛɪʏɔʊ])([.ˈ][h]?)((?=[aeɛiɪoɔuʊyʏ]))",
        lambda match: (
            tense_vowel.get(match.group(1), match.group(1)) + match.group(2)
        ),
    ),
    # But not before consonantal glides
    (r"ei̯", "ɛi̯"),
    (r"eu̯", "ɛu̯"),
    # Nasal vowels
    (
        rf"({classical_vowel})m$",
        lambda match: lax_vowel.get(match.group(1), match.group(1)) + TILDE + HALF_LONG,
    ),
    (
        rf"({classical_vowel})[nm]([.ˈ]?[sf])",
        lambda match: tense_vowel.get(match.group(1), match.group(1))
        + TILDE
        + LONG
        + match.group(2),
    ),
    # Dissimilation after homorganic glides (the tuom volgus-type)
    # (r"([wu])([.ˈ]?)([h]?)ʊ", r"\1\2\3o"),
    # (r"([ji])([.ˈ]?)([h]?)ɪ", r"\1\2\3e"),
    # Voicing and loss of intervocalic /h/.
    (r"([^ˈ].)h", r"\1(ɦ)"),
    # Per Allen (1978: 43–45).
    # Phonetic (as opposed to lexical/phonemic) assimilations
    # Place
    # First because this accounts for 'atque' seemingly escaping total assimilation (and 'adque' presumably not)
    (r"[d]([.ˈ]?)s", r"s\1s"),  # leave [t] out since etsi has [ts], not [sː]
    (r"s[^ː]([.ˈ]?)s(?=[ptk])", r"s(ː)\1"),
    (r"st([.ˈ])([^aeɛiɪoɔuʊyʏe̯u̯])", r"s(t)\1\2"),
    (
        r"d([.ˈ])([pkɡln])",
        r"\2\1\2",
    ),  # leave [r] out since dr does not assimilate, even when heterosyllabic (e.g. quadrans), except in prefixed words
    (r"b([.ˈ])([mf])", r"\2\1\2"),
    (r"s([.ˈ])f", r"f\1f"),
    # Regressive voicing assimilation in consonant clusters
    (
        r"([bdɡ])([.ˈ]?)((?=[ptksf]))",
        lambda match: devoicing.get(match.group(1), match.group(1)) + match.group(2),
    ),
    (
        r"([ptk])([.ˈ]?)((?=[bdɡ]))",
        lambda match: voicing.get(match.group(1), match.group(1)) + match.group(2),
    ),
    # Allophones of /l/
    (r"l", "ɫ̪"),
    (r"ɫ̪([.ˈ]?)ɫ̪", r"l\1lʲ"),
    (r"ɫ̪([.ˈ]?[iɪyʏ])", r"lʲ\1"),
    # Retracted /s/
    (r"s", "s̠"),
    # dental Z
    (r"z([aeɛiɪoɔuʊyʏ])", r"d͡z\1"),
    (r"z([.ˈ])z", r"z\1(d͡)z"),
    (r"z", "z̪"),
    # Dental articulations
    (r"t", "t̪"),
    (r"d", "d̪"),
    (r"n([.ˈ]?)([td])", r"n̪\1\2"),
    # Allophones of A
    (r"a", "ä"),
]

phonetic_rules_eccl = [
    (
        r"([aɛeiɔou][ː.ˈ]*)s([.ˈ]*)\b(?=[aɛeiɔou])",
        r"\1s̬\2",
    ),  # partial voicing of s between vowels
    (r"s([.ˈ]*)\b(?=[bdgmnlv])", r"z\1"),  # full voicing of s before voiced consonants
    (r"ek([.ˈ]*)s([aɛeiɔoubdgmnlv])", r"eɡ\1z\2"),  # voicing of the prefix ex-
    (r"kz", r"ɡz"),  # handles /ksˈl/ issue
    # Tapped R intervocalically and in complex onset
    # (r"([aɛeiɔou]ː?[.ˈ])r([aɛeiɔou]?)", r"\1ɾ\2"),
    # (r"([fbdgptk])r", r"\1ɾ"),
    (r"a", r"ä"),  # a is open and central
    # Dental articulations
    (r"n([.ˈ]?)([td])([^͡])", r"n̪\1\2\3"),  # assimilation of n to dentality
    (r"l([.ˈ]?)([td])([^͡])", r"l̪\1\2\3"),
    # Note: n might not be dental otherwise; it may be alveolar in most contexts in Italian.
    (
        r"t([^͡])",
        r"t̪\1",
    ),  # t is dental, except as the first element of a palatal affricate
    (
        r"d([^͡])",
        r"d̪\1",
    ),  # d is dental, except as the first element of a palatal affricate
    (r"t͡s", r"t̪͡s̪"),  # dental affricates
    (r"d͡z", r"d̪͡z̪"),  # dental affricates
    (r"t̪([.ˈ]?)t͡ʃ", r"t\1t͡ʃ"),
    (r"d̪([.ˈ]?)d͡ʒ", r"d\1d͡ʒ"),
    # End of words
    (r"lt$", r"l̪t̪"),
    (r"nt$", r"n̪t̪"),
    (r"t$", r"t̪"),
    (r"d$", r"d̪"),
    # Partial assimilation of l and n before palatal affricates, as in Italian
    (r"l([.ˈ]?)t͡ʃ", r"l̠ʲ\1t͡ʃ"),
    (r"l([.ˈ]?)d͡ʒ", r"l̠ʲ\1d͡ʒ"),
    (r"l([.ˈ]?)ʃ", r"l̠ʲ\1ʃ"),
    (r"n([.ˈ]?)t͡ʃ", r"n̠ʲ\1t͡ʃ"),
    (r"n([.ˈ]?)d͡ʒ", r"n̠ʲ\1d͡ʒ"),
    (r"n([.ˈ]?)ʃ", r"n̠ʲ\1ʃ"),
    # Other coda nasal assimilation, full and partial. Per Canepari, only applies to /n/ and not to /m/
    (r"n([.ˈ]?)([kɡ])", r"ŋ\1\2"),
    (r"n([.ˈ]?)([fv])", r"ɱ\1\2"),
]

lenition = {
    "ɡ": "ɣ",
    "d": "ð",
}

lengthen_vowel = {
    "a": "aː",
    "aː": "aː",
    "ɛ": "ɛː",
    "ɛː": "ɛː",
    "e": "eː",
    "eː": "eː",
    "i": "iː",
    "iː": "iː",
    "ɔ": "ɔː",
    "ɔː": "ɔː",
    "o": "oː",
    "oː": "oː",
    "u": "uː",
    "uː": "uː",
    "au̯": "aːu̯",
    "ɛu̯": "ɛːu̯",
    "eu̯": "eːu̯",
}

vowels = [
    "a",
    "ɛ",
    "e",
    "ɪ",
    "i",
    "ɔ",
    "o",
    "ʊ",
    "u",
    "y",
    "aː",
    "ɛː",
    "eː",
    "iː",
    "ɔː",
    "oː",
    "uː",
    "yː",
    "ae̯",
    "oe̯",
    "ei̯",
    "au̯",
    "eu̯",
]

onsets = [
    "b",
    "p",
    "pʰ",
    "d",
    "t",
    "tʰ",
    "β",
    "ɡ",
    "k",
    "kʰ",
    "kʷ",
    "ɡʷ",
    "kw",
    "ɡw",
    "t͡s",
    "t͡ʃ",
    "d͡ʒ",
    "ʃ",
    "f",
    "s",
    "z",
    "d͡z",
    "h",
    "l",
    "m",
    "n",
    "ɲ",
    "r",
    "j",
    "v",
    "w",
    "bl",
    "pl",
    "pʰl",
    "br",
    "pr",
    "pʰr",
    "dr",
    "tr",
    "tʰr",
    "ɡl",
    "kl",
    "kʰl",
    "ɡr",
    "kr",
    "kʰr",
    "fl",
    "fr",
    "sp",
    "st",
    "sk",
    "skʷ",
    "sw",
    "spr",
    "str",
    "skr",
    "spl",
    "skl",
]

codas = [
    "b",
    "p",
    "pʰ",
    "d",
    "t",
    "tʰ",
    "ɡ",
    "k",
    "kʰ",
    "β",
    "f",
    "s",
    "z",
    "l",
    "m",
    "n",
    "ɲ",
    "r",
    "j",
    "ʃ",
    "sp",
    "st",
    "sk",
    "spʰ",
    "stʰ",
    "skʰ",
    "lp",
    "lt",
    "lk",
    "lb",
    "ld",
    "lɡ",
    "lpʰ",
    "ltʰ",
    "lkʰ",
    "lf",
    "rp",
    "rt",
    "rk",
    "rb",
    "rd",
    "rɡ",
    "rpʰ",
    "rtʰ",
    "rkʰ",
    "rf",
    "mp",
    "nt",
    "nk",
    "mb",
    "nd",
    "nɡ",
    "mpʰ",
    "ntʰ",
    "nkʰ",
    "lm",
    "rl",
    "rm",
    "rn",
    "ps",
    "ts",
    "ks",
    "ls",
    "ns",
    "rs",
    "lks",
    "nks",
    "rks",
    "rps",
    "mps",
    "lms",
    "rls",
    "rms",
    "rns",
]

cons_ending_prefixes = [
    "ab",
    "ad",
    "circum",
    "con",
    "dis",
    "ex",
    "in",
    "inter",
    "ob",
    "per",
    "sub",
    "subter",
    "super",
    "trans",
    "trāns",
]

remove_macrons = {
    "ā": "a",
    "ē": "e",
    "ī": "i",
    "ō": "o",
    "ū": "u",
    "ȳ": "y",
}

macrons_to_breves = {
    "ā": "ă",
    "ē": "ĕ",
    "ī": "ĭ",
    "ō": "ŏ",
    "ū": "ŭ",
    # Unicode doesn't have breve-y
    "ȳ": "y" + BREVE,
}

remove_breves = {
    "ă": "a",
    "ĕ": "e",
    "ĭ": "i",
    "ŏ": "o",
    "ŭ": "u",
    # Unicode doesn't have breve-y
}

remove_ligatures = {
    "æ": "ae",
    "œ": "oe",
}

# NOTE: Everything is lowercased very early on, so we don't have to worry about capitalized letters.
short_vowels_string = "aeiouyăĕĭŏŭäëïöüÿ"  # no breve-y in Unicode
long_vowels_string = "āēīōūȳ"
vowels_string = short_vowels_string + long_vowels_string
vowels_c = f"[{vowels_string}]"
non_vowels_c = f"[^{vowels_string}]"


def rfind(word, pattern):
    return re.search(pattern, word)


def rsubn(string, pattern, repl):
    return re.subn(pattern, repl, string)


def ulower(string: str):
    """Just here for compatibility with Lua code"""
    return string.lower()


def usub(string, i, j):
    """Substring from index `i` to `j`"""
    if j is None:
        return string[i:]

    return string[i:j]


def ulen(word):
    """Just here for compatibility with Lua code"""
    return len(word)


def rsub(string, pattern, repl):
    """Version of `rsubn()` that discards all but the first return value"""
    if not string:
        return ""
    if isinstance(repl, dict):
        n_str = string
        for char in n_str:
            if char in repl.keys():
                n_str = n_str.replace(char, repl[char])
        return n_str
    else:
        return re.sub(pattern, repl, string)


def rsubb(string, pattern, repl):
    """Version of `rsubn()` that returns a 2nd argument boolean indicating whether a substitution was made."""
    res, nsubs = rsubn(string, pattern, repl)
    return res, nsubs > 0


def letters_to_ipa(word, phonetic, eccl, vul):
    """Converts word to IPA sequence without yet accounting for pronunciation rules"""
    phonemes = []

    ipa_letters_dict = (
        letters_ipa_eccl if eccl else letters_ipa
    )

    while ulen(word) > 0:
        longestmatch = ""

        for letter, ipa in ipa_letters_dict.items():
            if (
                ulen(letter) > ulen(longestmatch)
                and usub(word, 0, ulen(letter)) == letter
            ):
                longestmatch = letter

        if ulen(longestmatch) > 0:
            if ipa_letters_dict[longestmatch] == "ks":
                phonemes.append("k")
                phonemes.append("s")
            else:
                phonemes.append(ipa_letters_dict[longestmatch])
            word = usub(word, ulen(longestmatch), None)
        else:
            phonemes.append(usub(word, 0, 1))
            word = usub(word, 1, None)

    if eccl:
        for i in range(len(phonemes)):
            prev = (phonemes[i - 1] if i > 0 else None)
            cur = (phonemes[i],)
            next = (phonemes[i + 1] if i < len(phonemes) - 1 else None)
            if next and (cur == "k" or cur == "ɡ") and rfind(next, r"^[eɛi]ː?$"):
                if cur == "k":
                    if prev == "s":
                        prev = "ʃ"
                        cur = "ʃ"
                    else:
                        cur = "t͡ʃ"
                        if prev == "k":
                            prev = "t"
                else:
                    cur = "d͡ʒ"
                    if prev == "ɡ":
                        prev = "d"
            if cur == "q":
                cur = "k"
            if (
                cur == "t"
                and next == "i"
                and not (prev == "s" or prev == "t")
                and vowels[phonemes[i + 2]]
            ):
                cur = "t͡s"
            if cur == "z":
                if next == "z":
                    cur = "d"
                    next = "d͡z"
                else:
                    cur = "d͡z"
            if cur == "kʰ":
                cur = "k"
            if cur == "tʰ":
                cur = "t"
            if cur == "ɡ" and next == "n":
                cur = "ɲ"
                next = "ɲ"
    return phonemes


def get_onset(syll):
    consonants = []

    for char in syll:
        if char in vowels:
            break
        if char and char != "ˈ":
            consonants.append(char)
    
    return "".join(consonants)


def get_coda(syll):
    consonants = []

    for char in reversed(syll):
        if char and char in vowels:
            break
        consonants.insert(0, char)

    return "".join(list(filter(lambda x: x is not None, consonants)))


def get_vowel(syll):
    for char in syll:
        if char and char in vowels:
            return char
    return None


def split_syllables(remainder):
    syllables = []
    syll = []

    for phoneme in remainder:
        if phoneme == ".":
            if syll:
                syllables.append(syll)
                syll = []
            syllables.append(["."])
        elif phoneme == "ˈ":
            if syll:
                syllables.append(syll)
            syll = ["ˈ"]
        elif phoneme in vowels:
            syll.append(phoneme)
            syllables.append(syll)
            syll = []
        else:
            syll.append(phoneme)

    if syll:
        syllables.append(syll)

    for i, current in enumerate(syllables):
        if len(current) == 1 and current[0] == ".":
            syllables.pop(i)
        elif i > 0:
            previous = syllables[i - 1]
            onset = get_onset(current)
            while onset != "" and onset not in onsets:
                previous.append(current.pop(0))
                onset = get_onset(current)
            if get_coda(previous) == "" and (current[0] == "s" and (len(current) > 1 and current[1] not in vowels)):
                previous.append(current.pop(0))
            if not get_vowel(current):
                # Move current element to previous
                while current:
                    previous.append(current.pop(0))

                # Remove syllables[i]
                syllables.pop(i)

                # Check if syllables[i] exists and contains only a dot
                if i < len(syllables) and len(syllables[i]) == 1 and syllables[i][0] == ".":
                    syllables.pop(i)

    for syll in syllables:
        onset = get_onset(syll)
        coda = get_coda(syll)
        if onset != "" and onset not in onsets:
            print(f"[WARNING] Bad onset ({onset}) in function split_syllables")
        if coda != "" and coda not in codas:
            print(f"[WARNING] Bad coda ({coda}) in function split_syllables")

    return syllables


def phoneme_is_short_vowel(phoneme):
    return rfind(phoneme, r"^[aɛeiɔouy]$")


def detect_accent(syllables, is_prefix, is_suffix):
    """Detect the position of the tonic accent within the word (returns the index
    of the accented syllable, or `-1` if no accent)"""
    for i, syll in enumerate(syllables):
        for j, phoneme in enumerate(syll):
            if phoneme == "ˈ":
                syll.remove(phoneme)
                return i

    if is_prefix:
        return -1

    if is_suffix:
    # Count syllables containing vowels, excluding the first syllable if it has no vowel
        syllables_with_vowel = len(syllables) - (0 if get_vowel(syllables[0]) else 1)
        
        # If there are fewer than 2 vowel-containing syllables, there is no stress on the suffix
        if syllables_with_vowel < 2:
            return -1

        # If there are exactly 2 vowel-containing syllables, check the penultimate one
        if syllables_with_vowel == 2:
            penult = syllables[-2]  # Second-to-last syllable
            # If the last phoneme in the penultimate syllable is a short vowel, no suffix stress
            if phoneme_is_short_vowel(penult[-1]):
                return -1

    # Detect accent placement
    if len(syllables) > 2:
        # Check the penultimate syllable
        penult = syllables[-2]
        
        # If the penultimate syllable ends with a short vowel, stress is on the antepenultimate syllable
        if phoneme_is_short_vowel(penult[-1]):
            return len(syllables) - 3  # Antepenultimate syllable
        else:
            return len(syllables) - 2  # Penultimate syllable

    elif len(syllables) == 2:
        # Stress the first syllable in disyllabic words
        return 0  # Penultimate syllable (first in this case)

    elif len(syllables) == 1:
        # Mark stress on monosyllabic words to ensure stress-conditioned rules apply
        return 0  # Stress on the only syllable


@lru_cache(500) # Cache the last n converted words for faster conversions of next occurences of the same word
def convert_word(word: str, phonetic: bool, eccl: bool, vul: bool) -> str:
    """Converts a word to IPA.

    Args:
        word (str): The word to be converted
        phonetic (bool): Whether the transcription has to be phonetic (`True`) or phonemic (`False`)
        eccl (bool): Whether the transcription must use ecclesiastical Latin rules or not. If `True`, `vul` must be set to `False`
        vul (bool): Whether the transcription must use vulgar Latin rules or not. If `True`, `eccl` must be set to `False`
        
        If both `eccl` and `vul` are false, classical Latin rules will be used

    Returns:
        str: The corresponding IPA string
    """

    # Normalize w, i, j, u, v; do this before removing breves, so we keep the
    # ŭ in langŭī (perfect of languēscō) as a vowel.
    word = rsub(word, "w", "v")
    word = rsub(word, f"({vowels_c})v({non_vowels_c})", r"\1u\2")
    word = rsub(word, "qu", "qv")
    word = rsub(word, f"ngu({vowels_c})", "ngv\1")

    word = rsub(word, f"^i({vowels_c})", "j\1")
    word = rsub(word, f"^u({vowels_c})", "v\1")

    # We convert i/j between vowels to jj if the preceding vowel is short
    # but to single j if the preceding vowel is long.
    def repl_func(match):
        vowel = match.group(1)
        potential_consonant = match.group(2)
        pos = match.start()  # Start position of the match in the string

        # Check if the character at the position is in vowels_string
        if vowels_string.find(word[pos]) != -1:
            if potential_consonant == "u":
                if not rfind(word, rf"{vowels_c}us$"):
                    return vowel + "v"
            else:
                if long_vowels_string.find(vowel) != -1:
                    return vowel + "j"
                else:
                    return vowel + "jj"
        return match.group(0)  # If no replacement, return the original match
    
    word = rsub(word, f"({vowels_c})([iju])()", repl_func)

    # Convert v to u syllable-finally
    word = rsub(word, r"v\.", "u.")
    word = rsub(word, r"v$", "u")

    # Convert i to j before vowel and after any prefix that ends in a consonant
    for pref in cons_ending_prefixes:
        word = rsub(word, f"^({pref})i({vowels_c})", r"\1j\2")

    # Ecclesiastical has neither geminate j.j, nor geminate w.w in Greek words
    if eccl:
        word = rsub(word, f"({vowels_c})u([.ˈ]?)v({vowels_c})", r"\1\2v\3")
        word = rsub(word, f"({vowels_c})j([.ˈ]?)j({vowels_c})", r"\1\2j\3")

    # Convert z to zz between vowels so that the syllable weight and stress assignment will be correct.
    word = rsub(word, f"({vowels_c})z({vowels_c})", r"\1zz\2")

    if eccl:
        word = rsub(word, f"({vowels_c})ti({vowels_c})", r"\1tt͡si\2")

    # Now remove breves.
    word = rsub(word, r"([ăĕĭŏŭ])", remove_breves)
    word = rsub(word, BREVE, "")

    # Normalize aë, oë; do this after removing breves but before any
    # other normalizations involving e.
    word = rsub(word, r"([ao])ë", r"\1.e")

    # Eu and ei diphthongs
    word = rsub(word, r"e(u[ms])$", r"e.\1")
    word = rsub(word, "ei", "e.i")
    word = rsub(word, "_", "")

    # Vowel length before nasal + fricative is allophonic
    word = rsub(word, r"([āēīōūȳ])([mn][fs])", lambda m: remove_macrons[m.group(1)] + m.group(2))

    # Vowel before yod
    vowel_before_yod = {
        "a": "āj",
        "e": "ēj",
        "o": "ōj",
        "u": "ūj",
        "y": "ȳ",
    }
    if eccl:
        word = rsub(word, r"([aeouy])([j])", lambda m: vowel_before_yod[m.group(1)])

    # Apply some basic phoneme-level assimilations for Ecclesiastical, which reads as written;
    # in living varieties the assimilations were phonetic
    word = rsub(word, "xs", "x")

    # We syllabify prefixes ab-, ad-, ob-, sub- separately from following l or r.
    word = rsub(word, r"^a([bd])([lr])", r"a\1.\2")
    word = rsub(word, r"^ob([lr])", r"ob.\1")
    word = rsub(word, r"^sub([lr])", r"sub.\1")

    # Remove hyphens indicating prefixes or suffixes; do this after the above,
    # some of which are sensitive to beginning or end of word and shouldn't
    # apply to end of prefix or beginning of suffix.
    word, is_prefix = rsubb(word, r"-$", "")
    word, is_suffix = rsubb(word, r"^-", "")

    # Convert word to IPA
    phonemes = letters_to_ipa(word, phonetic, eccl, vul)

    # Split into syllables
    syllables = split_syllables(phonemes)

    # Add accent
    accent = detect_accent(syllables, is_prefix, is_suffix)
    
    # Poetic meter shows that a consonant before "h" was syllabified as an onset, not as a coda.
    # This will be indicated by the omission of /h/ [h] in this context.
    word = rsub(word, r"([^aeɛiɪoɔuʊyʏe̯u̯ptk])([.ˈ]?)h", r"\1")

    for i, syll in enumerate(syllables):
        for j, phoneme in enumerate(syll):
            if eccl or vul:
                syll[j] = rsub(syll[j], "ː", "")
            elif phonetic:
                syll[j] = lax_vowel.get(syll[j], syll[j])

    for i, syll in enumerate(syllables):
        if (eccl or vul) and i == accent and phonetic and (syll and syll[-1] in vowels):
            syll[-1] = lengthen_vowel.get(syll[-1], syll[-1])

        for j in range(len(syll) - 1):
            if syll[j] == syll[j + 1]:
                syll[j + 1] = ""

    # Atonic /ɔ/ and /ɛ/ merge with /o/ and /e/ respectively
    for i, syll in enumerate(syllables):
        syll = "".join(syll)
        if vul and i != accent:
            syll = rsub(syll, "ɔ", "o")
            syll = rsub(syll, "ɛ", "e")
        if eccl and phonetic and i == accent:
            syll = rsub(syll, "o", "ɔ")
            syll = rsub(syll, "e", "ɛ")
        syllables[i] = ("ˈ" if i == accent else "") + syll

    word = rsub(".".join(syllables), r"\.ˈ", "ˈ")

    # If single-syllable word, remove initial accent marks
    if len(syllables) == 1:
        word = rsub(word, r"^ˈ", "")

    if eccl:
        word = rsub(word, r"([^aeɛioɔu])ʃ([.ˈ]?)ʃ", r"\1\2ʃ")

    # Normalize glide spelling
    if not eccl:
        word = rsub(word, "j", "i̯")
        word = rsub(word, "w", "u̯")

    if phonetic:
        rules = phonetic_rules_eccl if eccl else phonetic_rules
        for rule in rules:
            word = rsub(word, rule[0], rule[1])

        word = rsub(word, r"\.", "")  # remove the dots! >_<

    # Normalize glide spelling for non-Ecclesiastical
    if not eccl:
        word = rsub(word, "j", "i̯")
        word = rsub(word, "w", "u̯")

    if phonetic:
        word = rsub(word, r"([a-zA-Z][̪̠̯]?)\1", r"\1" + LONG)
        word = rsub(word, "ːː", "ː")

    return word

def initial_canonicalize_text(text: str) -> str:
    """
    Canonicalize the text by removing specific punctuation and replacing ligatures.
    """
    text = ulower(text)  # Convert to lowercase
    text = rsub(text, r'[,?!:;()"]', '')  # Remove specified punctuation
    text = rsub(text, r'[æœ]', remove_ligatures)  # Replace ligatures
    return text

def convert_words(text: str, phonetic: bool, eccl: bool, vul: bool) -> str:
    """
    Process the input text and convert each word to IPA.
    
        Args:
        text (str): The text to be converted
        phonetic (bool): Whether the transcription has to be phonetic (`True`) or phonemic (`False`)
        eccl (bool): Whether the transcription must use ecclesiastical Latin rules or not. If `True`, `vul` must be set to `False`
        vul (bool): Whether the transcription must use vulgar Latin rules or not. If `True`, `eccl` must be set to `False`
        
        If both `eccl` and `vul` are false, classical Latin rules will be used.

    Returns:
        str: The corresponding IPA string
    """
    # Canonicalize the input text
    text = initial_canonicalize_text(text)

    # Check for disallowed characters
    allowed_chars = rf'[a-z\-āēīōūȳăĕĭŏŭë,.?!:;()\'"_ {BREVE}]'
    disallowed = rsub(text, allowed_chars, '')
    if ulen(disallowed) > 0:
        if ulen(disallowed) == 1:
            raise ValueError(f'The character "{disallowed}" is not allowed.')
        else:
            raise ValueError(f'The characters "{disallowed}" are not allowed.')
    
    # Process words
    result = []
    for word in text.split(" "):  # Split text into words
        result.append(convert_word(word, phonetic, eccl, vul))  # Convert each word

    # Join the results into a single string
    return " ".join(result)

def phoneticize(text: str, variant: Literal["eccl", "vul", "clas"] = "clas", phonetic = False) -> str | Tuple[str, str]:
    """Phoneticize a Latin text into IPA.

    Args:
        text (str): The text to be converted.
        variant (Literal[&quot;eccl&quot;, &quot;vul&quot;, &quot;clas&quot;], optional): The variant whose rules must be applied ([`eccl`]esiastic, [`vul`]gar, [`clas`]sical). Defaults to "clas".
        phonetic (bool, optional): Whether to return the phonetic transcription along with the phonemic one. False yields the phonemic transcription only, and True both the phonemic and phonetic one.

    Raises:
        ValueError: In case variant is not set to either "eccl", "vul" or "clas".

    Returns:
        str | Tuple[str, str]: If a string, the phonemic transcription. If a tuple of strings, the phonemic and phonetic transription, respectively.
    """
    if variant not in ["eccl", "vul", "clas"]:
        raise ValueError("Wrong variant! Must be either [eccl]esiastical, [vul]gar or [clas]sical.")
    
    if variant == "eccl":
        eccl = True
        vul = False
    elif variant == "vul":
        eccl = False
        vul = True
    else: # epoch == "clas"
        eccl = False
        vul = False
    
    text = ulower(text)
    text = rsub(text, r"\s", " ") # Replace newline feeds, tabs etc. by simple spaces
    
    if phonetic:
        return convert_words(text, False, eccl, vul), convert_words(text, True, eccl, vul)
    else: return convert_words(text, False, eccl, vul)