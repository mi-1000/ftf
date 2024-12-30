# [NOTE] Implementation of Lua functions used in the following modules in Python for easier transcription:
# https://en.wiktionary.org/wiki/Module:la-pronunc
# https://en.wiktionary.org/wiki/Module:grc-pronunciation
# [NOTE] These functions as is are unnecessary in Python and actually slightly worsen performance. They are here to facilitate the transcription of the original Lua code and should be refactored once everything is assured to be properly working.
# Last revision: 2024-12-23

import re
import unicodedata

from typing import Any

UNACCENTED_GREEK_LETTERS = "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"

def rfind(string, pattern):
    """Reimplementation of :func:`re.search` for compatibility with Lua code"""
    return re.search(pattern, string)


def rmatch(string, pattern, init = 0):
    """Return a tuple of matches for each capturing group against a given string and pattern, or an empty string if nothing was found."""
    if init >= len(string) or init < 0:
        return ""
    match = re.search(pattern, string[init:])
    return match.groups() if match else ""


def rsplit(string: str, pattern: str) -> list[str]:
    """Split a string according to a certain pattern (reimplementation of :func:`str.split` for compatibility with Lua code)"""
    return string.split(pattern)


def rsub(string: str, pattern: str, repl: Any) -> str:
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


def rsubb(string: str, pattern: str, repl: str) -> tuple[str, bool]:
    """Version of `rsubn()` that returns a 2nd argument boolean indicating whether a substitution was made."""
    res, nsubs = rsubn(string, pattern, repl)
    return res, nsubs > 0


def rsubn(string: str, pattern: str, repl: str) -> tuple[str, int]:
    """Reimplementation of :func:`re.subn` for compatibility with Lua code"""
    return re.subn(pattern, repl, string)


def ulen(word: str) -> int:
    """Length of word - Just here for compatibility with Lua code"""
    return len(word)


def ulower(string: str) -> str:
    """Lowercase string - Just here for compatibility with Lua code"""
    return string.lower()


def usub(string: str, i: int, j: int | None = None) -> str:
    """Substring from index `i` to `j` inclusive"""
    if j is None:
        return string[i:]

    return string[i:j+1]


def decompose(text: str) -> list[str]:
    """Decompse a string into its constituent characters and diacritics.

    Args:
        text (str): The text to be decomposed

    Returns:
        str: The decomposed text
    """
    return [char for char in unicodedata.normalize("NFKD", text)]


def strip_accent(text: str) -> str:
    """Strip accents from a Greek string.

    Args:
        text (str): The text to strip accents from.

    Returns:
        str: The text with accents stripped.
    """
    return "".join(char for char in decompose(text) if char in UNACCENTED_GREEK_LETTERS)

def strip_combining_accent(text:str) -> str:
    """Strip combining (standalone) accents, **i.e.** which cannot be combined with a base letter as a single character.

    Args:
        text (str): The text to strip combining accents from. 

    Returns:
        str: The text with combining accents stripped.
    """
    if len(text) == len(strip_accent(text)):
        return text # No combining accents
    
    chars = [x for x in text]
    stripped = [strip_accent(x) for x in text]
    for i, char in enumerate(chars):
        if not stripped[i]: # If character is a single (combining) diacritic
            chars.pop(i)
            stripped.pop(i) # Also remove from there to keep the lists in sync
    return "".join(chars)