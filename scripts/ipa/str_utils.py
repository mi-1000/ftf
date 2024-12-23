# [NOTE] Implementation of Lua functions used in the following modules in Python for easier transcription:
# https://en.wiktionary.org/wiki/Module:la-pronunc
# https://en.wiktionary.org/wiki/Module:grc-pronunciation
# [NOTE] These functions as is are unnecessary in Python and actually slightly worsen performance. They are here to facilitate the transcription of the original Lua code and should be refactored once everything is assured to be properly working.
# Last revision: 2024-12-23

import re
import unicodedata

from grc_data import ALL_DIACRITICS

def rfind(string, pattern):
    """Reimplementation of :func:`re.search` for compatibility with Lua code"""
    return re.search(pattern, string)


def rsubn(string, pattern, repl):
    """Reimplementation of :func:`re.subn` for compatibility with Lua code"""
    return re.subn(pattern, repl, string)


def ulower(string: str):
    """Lowercase string - Just here for compatibility with Lua code"""
    return string.lower()


def usub(string, i, j):
    """Substring from index `i` to `j`"""
    if j is None:
        return string[i:]

    return string[i:j]


def ulen(word):
    """Length of word - Just here for compatibility with Lua code"""
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


def decompose(text: str) -> str:
    """Decompses a string into its constituent characters and diacritics.

    Args:
        text (str): The text to be decomposed

    Returns:
        str: The decomposed text
    """
    return unicodedata.normalize("NFD", text)


def strip_accent(text: str) -> str:
    """Strip accents from a string.

    Args:
        text (str): The text to strip accents from.

    Returns:
        str: The text with accents stripped.
    """
    return "".join(char for char in decompose(text) if char not in ALL_DIACRITICS)
