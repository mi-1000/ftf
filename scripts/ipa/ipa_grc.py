# [NOTE] Implementation and free adaptation of the following Lua module from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:grc-pronunciation
# Last revision: 2024-12-23

from str_utils import decompose, rfind, strip_accent

from grc_data import (
    MACRON,
    BREVE,
    
    MODIFIER_MACRON,
    SPACING_BREVE,
    SPACING_MACRON,
    
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

    if "[" in char_set and "]" in char_set:  # If char_set is already a regex pattern
        pattern = f"^{pattern}$"
    else:
        pattern = f"^[{pattern}]$"

    return rfind(text, pattern)

env_functions = {
    # Character precedes a front vowel
    'preFront': lambda term, index: (
        is_of_type(strip_accent(fetch(term, index + 1)), "frontVowel") or
        (is_of_type(strip_accent(fetch(term, index + 1) + fetch(term, index + 2)), "frontDiphth") and not is_of_type(fetch(term, index + 2), "iDiaer"))
    ),
    
    # Character is part of a diphthong in i
    'isIDiphth': lambda term, index: (
        strip_accent(fetch(term, index + 1)) == 'ι' and not greek_data.get(fetch(term, index + 1), {}).get('diaer', False)
    ),
    
    # Character is part of a diphthong in u
    'isUDiphth': lambda term, index: (
        strip_accent(fetch(term, index + 1)) == 'υ' and not greek_data.get(fetch(term, index + 1), {}).get('diaer', False)
    ),
    
    # Character has a macron or breve diacritic
    'hasMacronBreve': lambda term, index: (
        any(char in [MACRON, SPACING_MACRON, MODIFIER_MACRON] for char in decompose(fetch(term, index)))
        or any(char in [BREVE, SPACING_BREVE] for char in decompose(fetch(term, index)))
    ),
}