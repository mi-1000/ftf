import re

def rfind(word, pattern):
    """Reimplementation of :func:`re.search` for compatibility with Lua code"""
    return re.search(pattern, word)


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