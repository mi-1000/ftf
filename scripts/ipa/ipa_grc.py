# [NOTE] Implementation and free adaptation of the following Lua module from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:grc-pronunciation
# Last revision: 2024-12-23

from functools import lru_cache
from typing import Literal
import unicodedata

from str_utils import decompose, rfind, rmatch, rsplit, rsub, strip_greek_accent, strip_combining_accent, strip_ipa_accent, ulen, usub

from grc_data import (
    ASPIRATED,
    BREVE,
    MACRON,
    MODIFIER_MACRON,
    NONSYLLABIC,
    PERIODS,
    SPACING_BREVE,
    SPACING_MACRON,
    TIE,
    VOICELESS,
    
    CHAR_SETS,
    
    get_data,
)

greek_data = get_data()

def fetch(string: str | bytes, i: int) -> str:
    """Fetch a character from a Unicode or byte string (reimplentation from original Lua function).

    Args:
        string (str): The string or bytestring.
        i (int): The index of the character to fetch.
    """
    if i < 0 or i >= len(string):  # If index is out of bounds
        return ""
    if isinstance(string, bytes):  # If string is a bstring
        string = string.decode("utf-8")  # Decode to Unicode
    return string[i]


def is_of_type(text: str, char_set: str):
    if not text or not char_set:
        return False

    pattern = CHAR_SETS.get(char_set)
    if not pattern:
        raise ValueError(
            f'No data for "{char_set}". Key must be one of the following: {list(CHAR_SETS.keys())}.'
        )

    if "[" in pattern and "]" in pattern:
        pattern = f"^{pattern}$"
    else:
        pattern = f"^[{pattern}]$"

    return rfind(text, pattern)

env_functions = {
    # Character precedes a front vowel
    'preFront': lambda term, index: (
        is_of_type(strip_greek_accent(fetch(term, index + 1)), "frontVowel") or
        (is_of_type(strip_greek_accent(fetch(term, index + 1) + fetch(term, index + 2)), "frontDiphth") and not is_of_type(fetch(term, index + 2), "iDiaer"))
    ),
    
    # Character is part of a diphthong in i
    'isIDiphth': lambda term, index: (
        strip_greek_accent(fetch(term, index + 1)) == 'ι' and not greek_data.get(fetch(term, index + 1), {}).get('diaer', False)
    ),
    
    # Character is part of a diphthong in u
    'isUDiphth': lambda term, index: (
        strip_greek_accent(fetch(term, index + 1)) == 'υ' and not greek_data.get(fetch(term, index + 1), {}).get('diaer', False)
    ),
    
    # Character has a macron or breve diacritic
    'hasMacronBreve': lambda term, index: (
        any(char in [MACRON, SPACING_MACRON, MODIFIER_MACRON] for char in decompose(fetch(term, index)))
        or any(char in [BREVE, SPACING_BREVE] for char in decompose(fetch(term, index)))
    ),
}

def decode(condition: str, x: int, term: str):
    """Decode a condition string within data.
    
    "If" and "and" statements.
    Note that we're finding the last operator first,
    which means that the first will get ultimately get decided first.
    If `+` ("*and*") or `/` ("*or*") is found, the function is called again,
    until if-statements are found.
    In if-statements:
    - A number represents the character under consideration:
        -1 is the previous character, 0 is the current, and 1 is the next.
    - Equals sign (=) checks to see if the character under consideration
        is equal to a character.
    - Period (.) plus a word sends the module to the corresponding entry
        in the letter's data table.
    - Tilde (~) calls a function on the character under consideration,
        if the function exists.
    """


    # Check for logical operators ('+' or '/')
    if rfind(condition, ('[+/]')):
        # Find the last operator first
        subcondition1, sep, subcondition2 = rmatch(condition, r"^([^/+]+)([/+])(.*)$")
        
        if not (subcondition1 or subcondition2):
            raise ValueError(f'Condition "{condition}" is improperly formed')

        if sep == '/': # Or
            return decode(subcondition1, x, term) or decode(subcondition2, x, term)
        elif sep == '+': # And
            return decode(subcondition1, x, term) and decode(subcondition2, x, term)

    # Check for character identity ('=')
    elif '=' in condition:
        offset, char = rsplit(condition, '=')
        offset = int(offset) # Ensure offset to an integer
        return char == fetch(term, x + offset)

    # Check for character quality ('.')
    elif '.' in condition:
        offset, quality = rsplit(condition, '.')
        offset = int(offset) # Ensure offset to an integer
        character = fetch(term, x + offset)
        return greek_data.get(character, {}).get(quality, False)

    # Check for function call ('~')
    elif '~' in condition:
        offset, func = rsplit(condition, '~')
        offset = int(offset) # Ensure offset to an integer
        return env_functions[func](term, x + offset) if env_functions.get(func) else False

def check(p, x: int, term: str):
    if isinstance(p, (str, int)): # If a number of chars to advance or a stringified number
        return p
    elif isinstance(p, (list, tuple)): # If conditional data to decode
        for possP in p:
            if isinstance(possP, (str, int)): # If nothing to decode anymore
                return possP
            elif isinstance(possP, (list, tuple)) and len(possP) == 2: # Table with two values (condition and result)
                raw_condition, raw_result = possP[0], possP[1]
                if decode(raw_condition, x, term): # Call decode() to check the condition
                    return raw_result if isinstance(raw_result, str) else check(raw_result, x, term)
    else:
        raise TypeError(f'"p" is of unrecognized type {type(p)}')

# @lru_cache(500) # Cache the last results of the function # TODO Fix this, I don't know why but this adds random syllable break points on words transcribed for the second time and more
def convert_term(term: str, periodstart: Literal['cla', 'koi1', 'koi2', 'byz1', 'byz2'] = 'cla') -> tuple[dict, list[Literal['cla', 'koi1', 'koi2','byz1', 'byz2']]]:
    if not term:
        raise ValueError('The variable "term" in the function "convert_term" is missing.')

    IPAs = {}
    outPeriods: list[Literal['cla', 'koi1', 'koi2', 'byz1', 'byz2']] = []

    # Determine if processing should start from the first period (classical) or after a specified one
    start = False if periodstart else True

    # Process periods to initialize IPA dictionaries
    for period in PERIODS:
        if period == periodstart:
            start = True
        if start:
            IPAs[period] = []
            outPeriods.append(period)

    length = ulen(term)
    x = 0

    while x < length:
        letter = fetch(term, x)
        data = greek_data.get(letter) or greek_data.get(strip_combining_accent(letter)) or greek_data.get(strip_greek_accent(letter)) # Check for data, and try to remove accents in case of encoding problems, despite potential loss of data (TODO)

        if data: # If data exists for the letter
            # Check if a multicharacter search is warranted
            advance = check(data.get('pre'), x, term) if 'pre' in data else 0
            advance = int(advance) if advance else 0

            # Determine pronunciation data (p)
            if advance != 0:
                p = greek_data[usub(term, x, x + advance)]['p']
            elif 'p' in data.keys(): # TODO Do more profound checks to see if we don't miss a letter
                p = data['p']
            else:
                raise ValueError(f'No data for "{letter}" at position {x}')
            # Process IPAs
            for period in outPeriods:
                IPAs[period].append(check(p[period], x, term))

            x += advance

        x += 1

    # Concatenate the IPA values into strings
    for period in outPeriods:
        IPAs[period] = ''.join(IPAs[period])

    return IPAs, outPeriods

def find_syllable_break(word: str, nVowel: int, wordEnd: bool) -> int:
    if not word:
        raise ValueError('The variable "word" in the function "find_syllable_break" is empty.')

    # If we're at the end of the word, we return the length of the word
    if wordEnd:
        return ulen(word)

    # We check conditions based on the type and position of characters
    if is_of_type(fetch(word, nVowel - 1), "liquid"):
        if is_of_type(fetch(word, nVowel - 2), "obst"):
            return nVowel - 3
        elif fetch(word, nVowel - 2) == ASPIRATED and is_of_type(fetch(word, nVowel - 3), "obst"):
            return nVowel - 4
        else:
            return nVowel - 2
    elif is_of_type(fetch(word, nVowel - 1), "cons"):
        return nVowel - 2
    elif fetch(word, nVowel - 1) == ASPIRATED and is_of_type(fetch(word, nVowel - 2), "obst"):
        return nVowel - 3
    elif fetch(word, nVowel - 1) == VOICELESS and fetch(word, nVowel - 2) == 'r':
        return nVowel - 3
    else:
        return nVowel - 1

def syllabify_word(word: str) -> str:
    # Initialize variables
    syllables = []
    current_vowel, next_vowel, syllable_break, stress, wordEnd, searching = None, None, None, False, False, None
    
    if not any(is_of_type(unicodedata.normalize("NFKD", char), "vowel") for char in word): # Word without any vowel
        return word
    
    while word:
        current_vowel, next_vowel, syllable_break, stress = None, None, None, False
        
        # Find the first vowel
        searching = 0
        cVowelFound = False
        while current_vowel is None:
            letter = fetch(word, searching)
            next_letter = fetch(word, searching + 1)
            if cVowelFound:
                if (is_of_type(letter, "vowel") and next_letter != NONSYLLABIC) or is_of_type(letter, "cons") or letter in ['', 'ˈ']:
                    current_vowel = searching - 1
                elif is_of_type(letter, "diacritic"):
                    searching += 1
                elif letter == TIE:
                    cVowelFound = False
                    searching += 1
                else:
                    searching += 1
            else:
                if is_of_type(letter, "vowel"):
                    cVowelFound = True
                elif letter == 'ˈ':
                    stress = True
                searching += 1
        
        # Find the next vowel or the end of the word
        searching = current_vowel + 1
        while next_vowel is None and not wordEnd:
            letter = fetch(word, searching)
            if is_of_type(letter, "vowel") or letter == 'ˈ':
                next_vowel = searching
            elif letter == '':
                wordEnd = True
            else:
                searching += 1
        
        # Find the syllable break point
        syllable_break = find_syllable_break(word, next_vowel, wordEnd)
        
        # Extract the syllable up to and including the break point
        syllable = usub(word, 0, syllable_break)
        
        # Adjust stress accents
        if stress:
            if syllables or syllable != word:
                syllable = 'ˈ' + rsub(syllable, 'ˈ', '')
            else:
                syllable = rsub(syllable, 'ˈ', '')
            stress = False
        
        # Add the syllable to the list
        syllables.append(syllable)
        word = usub(word, syllable_break + 1)
    
    # Concatenate syllables with periods
    out = ""
    if len(syllables) > 0:
        out = '.'.join(syllables)
        out = rsub(out, r'\.ˈ', 'ˈ')
    return out


def syllabify(IPAs, periods):
    for period in periods:
        ipa = []
        for word in rsplit(IPAs[period], ' '):
            word_ipa = syllabify_word(word)
            if word_ipa:
                ipa.append(word_ipa)
        IPAs[period] = ' '.join(ipa)
    return IPAs

def phoneticize(text: str, period: Literal['cla', 'koi1', 'koi2', 'byz1', 'byz2'] = 'cla') -> str:
    
    words = filter(lambda x: rfind(x, r"\w"), text.split())
    phon = []
    for word in words:
        phon.append(syllabify(*convert_term(unicodedata.normalize("NFKC", strip_combining_accent(word).lower())))[period])
    return " ".join(phon)

# if __name__ == "__main__":
    # tests = ["ἄγριος", "ἀκούω", "ἄναρθρος", "ἄνθρωπος", "ἄνθρωπος", "ἀρχιμανδρίτης", "Αὖλος", "Γάδ", "γαῖα", "γένος", "Διονύσια", "ἐγγενής", "ἔγγονος", "ἔγκειμαι", "ἔκγονος", "ἔκδικος", "ἐκφύω", "ἔμβρυον", "ἐρετμόν", "ἐρρήθη", "εὔχωμαι", "Ζεύς", "Ἡρακλέης", "ηὗρον", "Θρᾷξ", "Κιλικία", "μάχη", "ναῦς", "νομίζω", "οἷαι", "πᾶς", "πατρίς", "Πηληϊάδης", "πρᾶγμα", "Σαπφώ", "σβέννυμι", "σημεῖον", "σμικρός", "τάττω", "τὴν ἀοιδήν", "τμῆμα", "φιλίᾳ", "χάσμα", "χέω", "ᾠδῇ", "κέλευσμα"]

    # for test in tests:
    #     print(f"{test} : {phoneticize(test)}")

    # with open("data/raw/data_ancient_greek/Aristote,_Les_Topiques,_livre_I_greek.txt", 'r', encoding='utf-8') as f:
    #     lines = f.readlines()
    #     for period in PERIODS:
    #         print("".center(60, "="), f" {period.upper()} ".center(60, "="), "".center(60, "="), sep='\n')
    #         for i, line in enumerate(lines, 1):
    #             print(i, phoneticize(line, period))