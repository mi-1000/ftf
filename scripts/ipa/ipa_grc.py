# [NOTE] Implementation and free adaptation of the following Lua module from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:grc-pronunciation
# Last revision: 2024-12-23

import pprint
from typing import Literal

from str_utils import decompose, rfind, rmatch, strip_accent, ulen, usub

from grc_data import (
    MACRON,
    BREVE,
    MODIFIER_MACRON,
    SPACING_BREVE,
    SPACING_MACRON,
    
    CHAR_SETS,
    
    PERIODS,
    
    get_data,
)

greek_data = get_data()

pprint.pprint(greek_data)


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
        subcondition1, sep, subcondition2 = rmatch(condition, r"^([^/+]-)([/+])(.*)$")
        
        if not (subcondition1 or subcondition2):
            raise ValueError(f'Condition "{condition}" is improperly formed')

        if sep == '/': # Or
            return decode(subcondition1, x, term) or decode(subcondition2, x, term)
        elif sep == '+': # And
            return decode(subcondition1, x, term) and decode(subcondition2, x, term)

    # Check for character identity ('=')
    elif '=' in condition:
        offset, char = condition.split('=', 1)
        offset = int(offset)  # Convert offset to an integer
        return char == fetch(term, x + offset)  # Out of bounds fetch gives ''

    # Check for character quality ('.')
    elif '.' in condition:
        offset, quality = condition.split('.', 1)
        offset = int(offset)  # Convert offset to an integer
        character = fetch(term, x + offset)
        return greek_data.get(character, {}).get(quality, False)

    # Check for function call ('~')
    elif '~' in condition:
        offset, func = condition.split('~', 1)
        offset = int(offset)  # Convert offset to an integer
        # Assuming env_functions is a dictionary
        return env_functions[func](term, x + offset) if env_functions.get(func) else False

def check(p, x: int, term: str):
    if isinstance(p, (str, int)): # Check if p is a string or number
        return p
    elif isinstance(p, (list, tuple)): # Check if p is a list or a tuple
        for possP in p:
            if isinstance(possP, (str, int)): # If entry is a string or number
                return possP
            elif isinstance(possP, list) and len(possP) == 2: # Table with two values (condition and result)
                raw_condition, raw_result = possP[0], possP[1]
                if decode(raw_condition, x, term): # Call decode() to check the condition
                    return raw_result if isinstance(raw_result, str) else check(raw_result, x, term)
    else:
        raise TypeError(f'"p" is of unrecognized type {type(p)}')

def convert_term(term: str, periodstart: Literal['cla', 'koi1', 'koi2', 'byz1', 'byz2'] = 'cla'):
    if not term:
        raise ValueError('The variable "term" in the function "convert_term" is missing.')

    IPAs = {}
    outPeriods = []

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
        data = greek_data.get(letter)

        if data: # If data exists for the letter
            # Check if a multicharacter search is warranted
            advance = check(data.get('pre'), x, term) if 'pre' in data else 0

            # Determine pronunciation data (p)
            if advance != 0:
                p = greek_data[usub(term, x, x + advance)]['p']
            else:
                p = data['p']

            # Process IPAs
            for period in outPeriods:
                IPAs[period].append(check(p[period], x, term))

            x += advance

        x += 1

    # Concatenate the IPA values into strings
    for period in outPeriods:
        IPAs[period] = {'IPA': ''.join(IPAs[period])}

    return IPAs, outPeriods

print(convert_term('τῆλε', 'cla'))