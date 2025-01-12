# [NOTE] Implementation and free adaptation of the following Lua module from Wikipedia in Python:
# https://en.wiktionary.org/wiki/Module:fr-pron
# Last revision: 2025-01-02

# TODO Implement automatic respelling using trained model once ready?

import json
import re
import requests

from typing import Literal

from .str_utils import pattern_escape, rfind, rmatch, rsub, rsub_repeatedly, ulower

WEBSITE_URL = "http://127.0.0.1:5000" # localhost Flask server now

TILDE = "\u0303"  # Combining tilde =  ̃

# Invisible characters used as markers
EXPLICIT_H = "\uFFF0"
EXPLICIT_X = "\uFFF1"
EXPLICIT_J = "\uFFF2"

explicit_sound_to_substitution = {
    "h": EXPLICIT_H,
    "x": EXPLICIT_X,
    "j": EXPLICIT_J,
}

explicit_substitution_to_sound = {}
explicit_substitution_regex = []

for _from, to in explicit_sound_to_substitution.items():
    explicit_substitution_to_sound[to] = _from
    explicit_substitution_regex.append(to)

explicit_substitution_regex = f"[{''.join(explicit_substitution_regex)}]"

# Pairs of consonants where a schwa between them cannot be deleted in VCəCV
# within a word
no_delete_schwa_in_vcvcv_word_internally_list = ["ʁʁ", "ɲʁ", "ɲl"]

# Generate set
no_delete_schwa_in_vcvcv_word_internally = {
    x: True for x in no_delete_schwa_in_vcvcv_word_internally_list
}

# Pairs of consonants where a schwa between them cannot be deleted in VCəVC
# across a word boundary; primarily, consonants that are the same except
# possibly for voicing
no_delete_schwa_in_vcvcv_across_words_list = [
    "kɡ",
    "ɡk",
    "kk",
    "ɡɡ",  # ! WARNING: IPA ɡ used here
    "td",
    "dt",
    "tt",
    "dd",
    "bp",
    "pb",
    "pp",
    "bb",
    "ʃʒ",
    "ʒʃ",
    "ʃʃ",
    "ʒʒ",
    "fv",
    "vf",
    "ff",
    "vv",
    "sz",
    "zs",
    "ss",
    "zz",
    "jj",
    "ww",
    "ʁʁ",
    "ll",
    "nn",
    "ɲɲ",
    "mm",
    # FIXME, should be others
]

# Generate set
no_delete_schwa_in_vcvcv_across_words = {
    x: True for x in no_delete_schwa_in_vcvcv_across_words_list
}

remove_diaeresis_from_vowel = {
    "ä": "a",
    "ë": "e",
    "ï": "i",
    "ö": "o",
    "ü": "u",
    "ÿ": "i",
}


def allow_onset_2(c1: str, c2: str):
    """
    `True` if consonants `c1` and `c2` form an allowable onset (in which case we always
    attempt to place them after the syllable break)
    """
    # ! WARNING: We use both IPA and non-IPA g below, and both r and ʁ, because it is called both before and after the substitutions of these chars.
    return (
        (c2 in ["l", "r", "ʁ"] and rfind(r"[bkdfgɡpstv]", c1))
        or (c1 == "d" and c2 == "ʒ")
        or (c1 != "j" and c2 in ["j", "w", "W", "ɥ"])
    )


# List of vowels, including both input Latin and output IPA; note that
# IPA nasal vowels are two-character sequences with a combining tilde,
# which we include as the last char
oral_vowel_no_schwa_no_i = "aeouAEOUéàèùâêôûäëöüăōŭɑɛɔæœø"
oral_vowel_schwa = "əƏĕė"
oral_vowel_i = "iyIYîŷïÿ"
oral_vowel = oral_vowel_no_schwa_no_i + oral_vowel_schwa + oral_vowel_i
nasal_vowel = TILDE
non_nasal_c = f"[^{TILDE}]"
vowel_no_schwa = oral_vowel_no_schwa_no_i + oral_vowel_i + nasal_vowel
vowel = oral_vowel + nasal_vowel
vowel_c = f"[{vowel}]"
vowel_no_schwa_c = f"[{vowel_no_schwa}]"
vowel_maybe_nasal_r = f"[{oral_vowel}]{TILDE}?"
non_vowel_c = f"[^{vowel}]"
oral_vowel_c = f"[{oral_vowel}]"
# FIXME: Previously vowel_no_i specified the vowels explicitly and didn't include the nasal combining diacritic;
# should we include it?
vowel_no_i = oral_vowel_no_schwa_no_i + oral_vowel_schwa
vowel_no_i_c = f"[{vowel_no_i}]"
# Special characters that should be carried through but largely ignored when
# syllabifying; single quote prevents interpretation of sequences,
# ‿ indicates liaison, ⁀ is a word boundary marker, - is a literal hyphen
# (we include word boundary markers because they mark word boundaries with
# words joined by hyphens, but should be ignored for syllabification in
# such a case), parentheses are used to explicitly indicate an optional sound,
# especially a schwa
syljoiner_c = r"[_'‿⁀\-()]"  # Don't include syllable marker or space
opt_syljoiners_c = syljoiner_c + "*"
schwajoiner_c = r"[_'‿⁀\-. ]"  # Also include . and space but not ()
opt_schwajoiners_c = schwajoiner_c + r"*"
cons_c = rf"[^{vowel}.⁀ \-]"  # Includes underscore, quote and liaison marker
cons_no_liaison_c = (
    rf"[^{vowel}.⁀‿ \-]"  # Includes underscore and quote but not liaison marker
)
real_cons_c = rf"[^{vowel}_'‿.⁀ \-()]"  # Excludes underscore, quote and liaison marker
cons_or_joiner_c = rf"[^{vowel}. ]"  # Includes all joiners
front_vowel = r"eiîéèêĕėəɛæœyŷ"  # Should not include capital E, used in cœur etc.
front_vowel_c = rf"[{front_vowel}]"
word_begin = r"'‿⁀\-"  # Characters indicating the beginning of a word
word_begin_c = rf"[{word_begin}]"


def canonicalize_pron(text: str) -> str:
    text = rsub(text, "’", repl="'")
    text = rsub(text, r"(\d+),(\d+)", r"\1 virgule \2")
    text = rsub(text, r"[%]", " poursan ")
    text = rsub(text, r"[&]", " et ")
    text = rsub(text, r"[@]", " arobaz ")
    text = rsub(text, r"[€]", " euro ")
    text = rsub(text, r"[\$]", " dolar ")
    text = rsub(text, r"[£]", " livre sterling ")
    text = rsub(text, r"[!\?,;\.:/!§\*\{\}\[\]#\\\+=²°\"‘’“”­­­­­«»]", "") # Remove punctuation
    
    text = rsub(text, r"\s+", " ") # Replace newline feeds, tabs, carriage returns etc. by a space
    
    disallowed_chars = rf"[^{vowel}bcçdfghjklmnpqrstvwxz~_\'⁀‿\-]"
    rsub(text, disallowed_chars, "")

    # Replace explicit sounds in square brackets
    def repl_explicit_sounds(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 1:
            return "".join([str(match) for match in matches])
        sound = matches[0]
        return explicit_sound_to_substitution[ulower(sound)]
    text = rsub(
        text,
        r"\[([hHxXjJ])\]",
        repl_explicit_sounds
    )

    # Process substitutions if text is in square brackets
    if rfind(text, r"^\[.*\]$"):
        subs = rmatch(text, r"^\[(.*)\]$").split(",")
        for sub in subs:
            fromto = sub.split(":")
            if len(fromto) != 2:
                raise ValueError(
                    f"Bad substitution spec {sub} in function canonicalize_pron()"
                )

            _from, to = fromto[0], fromto[1]

            # Handle legacy ~ for matching within a word # TODO Keep it?
            if rfind(_from, r"^~"):
                _from = rmatch(_from, r"^~(.*)$")

            newtext = text

            if rfind(_from, r"^\^"):
                # Whole-word match
                _from = rmatch(_from, r"^\^(.*)$")
                pattern = r"(?<!\w)" + pattern_escape(_from) + r"(?!\w)"
                newtext = rsub(text, pattern, to)
            else:
                # General substitution
                pattern = pattern_escape(_from)
                newtext = rsub(text, pattern, to)

            if newtext == text:
                raise ValueError(
                    f"Substitution spec {sub} didn't match respelling '{text}'"
                )

            text = newtext

    # Convert text to lowercase
    text = ulower(text)
    return text

def convert(text: str) -> str:
    text = canonicalize_pron(text)
    
    if not text: return ""

    # To simplify checking for word boundaries and liaison markers, we
    # add ⁀ at the beginning and end of all words, and remove it at the end.
    # Note that the liaison marker is ‿.
    text = rsub(text, r"\s*,\s*", "⁀⁀ | ⁀⁀")
    text = rsub(text, r"\s+", "⁀ ⁀")
    text = rsub(text, r"\-+", "⁀-⁀")
    text = f"⁀⁀{text}⁀⁀"

    # Various early substitutions
    text = rsub(text, "ǝ", "ə")  # Replace wrong schwa with same-looking correct one
    text = rsub(text, "œu", "Eu")  # Capital E so it doesn't trigger c -> s
    text = rsub(text, "oeu", "Eu")
    text = rsub(text, "œil", "Euil")
    text = rsub(text, "œ", "æ")  # Keep as æ, mapping later to è or é

    # Silent final letters
    text = replace_on_pos(text, ["VERB", "NOUN"], r"[dt]\b", "")
    text = replace_on_pos(text, ["PROPN", "NOUN"], r"phe\b", "ph")

    # Handle soft c, g. Do these near the very beginning before any changes
    # that disturb the orthographic front/back vowel distinction (e.g.
    # -ai -> -é when pos == "v" in the next section); but after special
    # handling of œu (which should not trigger softening, as in cœur), whereas
    # other occurrences of œ do trigger softening (cœliaque).
    text = rsub(text, rf"c('?{front_vowel_c})", r"ç\1")
    text = rsub(text, r"ge([aoAOàâôäöăŏɔ])", r"j\1")
    text = rsub(text, rf"g(" + front_vowel_c + ")", r"j\1")

    # Special case for verbs
    text = replace_on_pos(text, "VERB", r"ai⁀", r"é⁀")
    # portions, retiens as verbs should not have /s/
    text = replace_on_pos(text, "VERB", r"ti([oe])ns([⁀‿])", r"t_i\1ns\2")
    # retienne, retiennent as verbs should not have /s/
    text = replace_on_pos(text, "VERB", r"t(ienne[⁀‿])", r"t_\1")
    text = replace_on_pos(text, "VERB", r"t(iennent[⁀‿])", r"t_\1")
    # Final -ent is silent except in single-syllable words (ment, sent);
    # vient, tient, and compounds will have to be special-cased, no easy
    # way to distinguish e.g. initient (silent) from retient (not silent).
    # TODO Unless we can lemmatize the word with Spacy and match infinitives that end in -enir :)
    text = replace_on_pos(text, "VERB", rf"({vowel_c}{cons_no_liaison_c}*)ent⁀", r"\1e⁐")
    text = replace_on_pos(text, "VERB", rf"({vowel_c}{cons_no_liaison_c}*)ent‿", r"\1ət‿")

    # Various early substitutions #2
    text = rsub(text, r"[aä]([sz][⁀‿])", r"â\1") # pas, gaz
    text = rsub(text, "à", "a")
    text = rsub(text, "ù", "u")
    text = rsub(text, "î", "i")
    text = rsub(text, r"[Ee]û", "ø")
    text = rsub(text, "û", "u")
    # absolute, obstacle, subsumer, obtus, obtenir, etc.; but not toubibs
    text = rsub(text, r"b([st][^⁀‿])", r"p\1")
    text = rsub(text, "ph", "f")
    text = rsub(text, "gn", "ɲ")
    text = rsub(text, "compt", "cont")
    text = rsub(text, "psych", "psik")

    # -chrom-, -chron-, chrétien, etc.; -chlor-, etc.; -techn-, arachn-, etc.; use 'sh' to get /ʃ/
    text = rsub(text, r"ch([rln])", r"c\1")

    # dinosaure, taure, restaurant, etc.; in unstressed syllables both /ɔ/ and /o/ are usually possible,
    # but /ɔ/ is more common/natural; not in -eaur-, which occurs in compounds e.g. Beauregard
    text = rsub(text, r"([^e])aur", r"\1or")
    text = rsub(text, rf"({word_begin_c})désh", r"\1déz")
    text = rsub(text, rf"({word_begin_c})et([⁀‿])", r"\1é\2")
    text = rsub(text, rf"({word_begin_c})es([⁀‿])", r"\1ès\2")
    text = rsub(text, rf"({word_begin_c})est([⁀‿])", r"\1èt\2")
    text = rsub(text, rf"({word_begin_c})ress", r"\1rəss") # ressortir, etc. should have schwa
    text = rsub(text, rf"({word_begin_c})intrans({vowel_c})", r"\1intranz\2")
    text = rsub(text, rf"({word_begin_c})trans({vowel_c})", r"\1tranz\2")
    text = rsub(text, rf"({word_begin_c})eu", r"\1ø")  # even in euro-
    text = rsub(text, rf"({word_begin_c})neur", r"\1nør")  # neuro-, neuralgie, etc.

    # hyperactif, etc.; without this we get /i.pʁak.tif/ etc.
    text = rsub(text, rf"({word_begin_c})hyper", r"\1hypèr")

    # superessif, etc.; without this we get /sy.pʁɛ.sif/ etc.
    text = rsub(text, rf"({word_begin_c})super", r"\1supèr")

    # Adverbial -emment is pronounced -amment
    text = replace_on_pos(text, "ADV", r"emment\b", r"ammen")

    text = rsub(text, r"ie(ds?[⁀‿])", r"illé\1") # pied, assieds, etc.
    text = rsub(text, r"[eæ]([dgpt]s?[⁀‿])", r"è\1") # permet
    text = rsub(text, r"ez([⁀‿])", r"é\1") # assez, avez, etc.
    text = rsub(text, r"er‿", r"èr‿") # premier étage
    text = rsub(text, rf"([⁀‿]{cons_c}*)er(s?[⁀‿])", r"\1èr\2") # cher, fer, vers
    text = rsub(text, r"er(s?[⁀‿])", r"ér\1") # premier(s)
    text = rsub(
        text, rf"({word_begin_c}{cons_c}*)e(s[⁀‿])", r"\1é\2"
    )  # ses, tes, etc.
    text = rsub(text, r"oien", r"oyen")  # iroquoien

    # bien, européens, païen, moyen; only word finally or before final s
    # (possibly in liaison); doesn't apply to influence, omniscient, réengager,
    # etc.; cases where -ien- is [jɛ̃] elsewhere in the word require respelling
    # using 'iain' or 'ien-', e.g. 'tient', 'viendra', 'bientôt', 'Vientiane'
    text = rsub(text, r"([iïéy])en(s?[⁀‿])", r"\1ɛn\2")
    # Special case for words beginning with bien- (bientôt, bienvenu, bienheureux, etc.)
    text = rsub(text, rf"({word_begin_c})bien", r"\1biɛn")

    # s, c, g, j, q (soft c/g handled above; ç handled below after dropping
    # silent -s; x handled below)
    text = rsub(text, r"cueil", r"keuil")  # accueil, etc.
    text = rsub(text, r"gueil", r"gueuil")  # orgueil
    text = rsub(text, rf"({vowel_c})s({vowel_c})", r"\1z\2")
    text = rsub(text, r"qu'", r"k'")  # qu'on
    text = rsub(text, rf"qu({vowel_c})", r"k\1")

    def gu_vowel(match: re.Match):
        vowel = match.group(1)
        vowel_without_diaeresis = remove_diaeresis_from_vowel.get(vowel)
        return f"gu{vowel_without_diaeresis}" if vowel_without_diaeresis else f"g{vowel}"
    # gu+vowel -> g+vowel, but gu+vowel+diaeresis -> gu+vowel
    text = rsub(
        text,
        f"gu({vowel_c})",
        gu_vowel
    )
    text = rsub(text, "gü", "gu")  # aiguë might be spelt aigüe
    # parking, footing etc.; also -ing_ e.g. swinguer respelt swing_guer,
    # Washington respelt Washing'tonne
    text = rsub(text, rf"({cons_c})ing(s?[_'⁀‿])", r"\1iŋ\2")
    text = rsub(text, r"ngt", r"nt")  # vingt, longtemps
    text = rsub(text, r"j", r"ʒ")
    text = rsub(text, r"s?[cs]h", r"ʃ")
    text = rsub(text, r"[cq]", r"k")
    # following two must follow s -> z between vowels
    text = rsub(text, r"([^sçx⁀])ti([oeɛ])n", r"\1si\2n")  # tion, tien
    text = rsub(text, r"([^sçx⁀])ti([ae])l", r"\1si\2l")  # tial, tiel

    # Special hack for uï; must follow guï handling and precede ill handling
    text = rsub(text, r"uï", r"ui")  # ouir, etc.

    # Special hack for oel, oil, oêl; must follow intervocal s -> z and
    # ge + o -> j, and precede -il- handling
    text = rsub(text, r"o[eê]l", r"wAl")  # moelle, poêle
    # poil but don't affect -oill- (otherwise interpreted as /ɔj/)
    text = rsub(text, r"oil([^l])", r"wAl\1")

    # ill, il; must follow j -> ʒ above
    # NOTE: In all of the following, we purposely do not check for a vowel
    # following -ill-, so that respellings can use it before a consonant
    # (e.g. boycotter respelt 'boillcotter')
    # (1) special-casing for C+uill (juillet, cuillère, aiguille respelt
    #     aiguïlle)
    text = rsub_repeatedly(text, rf"({cons_c})uill", r"\1ɥij")
    # (2) -ill- after a vowel; repeat if necessary in case of VillVill
    #     sequence (ailloille respelling of ayoye)
    text = rsub_repeatedly(text, rf"({vowel_c})ill", r"\1j")
    # (3) any other ill, except word-initially (illustrer etc.)
    text = rsub(text, r"([^⁀])ill", r"\1ij")
    # (4) final -il after a vowel; we consider final -Cil to contain a
    #     pronounced /l/ (e.g. 'il', 'fil', 'avril', 'exil', 'volatil', 'profil')
    text = rsub(text, rf"({vowel_c})il([⁀‿])", r"\1j\2")
    # (5) -il- after a vowel, before a consonant (not totally necessary;
    #     unlikely to occur normally, respelling can use -ill-)
    text = rsub(text, rf"({vowel_c})il({cons_c})", r"\1j\2")

    # y; include before removing final -e so we can distinguish -ay from
    # -aye
    text = rsub(text, r"ay([⁀‿])", r"ai\1") # gamay
    text = rsub(text, r"éy", "éj")  # Used in respellings, equivalent to 'éill'
    text = rsub(text, rf"({vowel_no_i_c})y", r"\1iy")
    text = rsub(text, rf"yi([{vowel}.])", r"y.y\1")
    text = rsub(text, "'y‿", "'j‿") # il n'y‿a
    text = rsub_repeatedly(text, f"({cons_c})y({cons_c})", r"\1i\2")
    text = rsub(text, rf"({cons_c})ye?([⁀‿])", r"\1i\2")
    text = rsub(text, rf"({word_begin_c})y({cons_c})", r"\1i\2")
    text = rsub(text, r"⁀y⁀", "⁀i⁀")
    # CyV -> CiV; will later be converted back to /j/ in most cases, but
    # allows correct handling of embryon, dryade, cryolithe, glyoxylique, etc.
    text = rsub(text, f"({cons_c})y({vowel_c})", r"\1i\2")
    text = rsub(text, "y", "j")

    # Nasal hacks
    # Make 'n' before liaison in certain cases both nasal and pronounced
    text = rsub(text, rf"({word_begin_c}[mts]?on)‿", r"\1N‿")  # mon, son, ton, on
    text = rsub(text, r"('on)‿", r"\1N‿")  # qu'on, l'on
    text = rsub(text, r"([eɛu]n)‿", r"\1N‿")  # en, bien, un, chacun etc.
    # In bon, certain etc. the preceding vowel isn't nasal
    text = rsub(text, r"n‿", r"N‿")

    # Other liaison hacks
    text = rsub(text, r"d‿", r"t‿")  # grand arbre, pied-à-terre
    text = rsub(
        text, r"[sx]‿", r"z‿"
    )  # vis-à-vis, beaux-arts, premiers enfants, etc.
    text = rsub(text, r"f‿", r"v‿")  # neuf ans, etc.
    # Treat liaison consonants that would be dropped as if they are extra-word,
    # so that preceding "word-final" letters are still dropped and preceding
    # vowels take on word-final qualities
    text = rsub(text, r"([bdgkpstxz]‿)", r"⁀\1")
    text = rsub(text, r"i‿", r"ij‿")  # y a-t-il, gentil enfant

    # Silent letters
    # Do this first so we also drop preceding letters if needed
    text = rsub(text, r"[sz]⁀", r"⁀")
    # Final -x silent in prix, chevaux, eux (with eu -> ø above)
    text = rsub(text, r"([iuø])x⁀", r"\1⁀")
    # Silence -c and -ct in nc(t), but not otherwise
    text = rsub(text, r"nkt?⁀", f"n⁀")
    text = rsub(text, r"([ks])t⁀", r"\1T⁀") # final -kt, -st pronounced
    text = rsub(text, r"ér⁀", r"é⁀") # premier, converted earlier to premiér
    # p in -mp, b in -mb will be dropped, but temporarily convert to capital
    # letter so a trace remains below when we handle nasals
    def repl_bp(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 1:
            return "".join([str(match) for match in matches])
        bp = matches[0]
        return f"m{bp.upper() if bp in ['b', 'p'] else ''}⁀"
    text = rsub(text, r"m([bp])⁀", repl_bp) # plomb
    # Do the following after dropping r so we don't affect -rt
    text = rsub(text, r"[dgpt]⁀", r"⁀")
    # Remove final -e in various circumstances; leave primarily when
    # preceded by two or more distinct consonants; in V[mn]e and Vmme/Vnne,
    # use [MN] so they're pronounced in full
    text = rsub(text, rf"({vowel_c})n+e([⁀‿])", r"\1N\2")
    text = rsub(text, rf"({vowel_c})m+e([⁀‿])", r"\1M\2")
    text = rsub(text, rf"({cons_c})\1e([⁀‿])", r"\1\2")
    text = rsub(text, rf"([mn]{cons_c})e([⁀‿])", r"\1\2")
    text = rsub(text, rf"({vowel_c}{cons_c}?)e([⁀‿])", r"\1\2")

    # ç; must follow s -> z between vowels (above); do after dropping final s
    # so that ç can be used in respelling to force a pronounced s
    text = rsub(text, "ç", "s")

    # x; (h)ex- at beginning of word (examen, exister, hexane, etc.) and after
    # a vowel (coexister, réexaminer) and after in- (inexact, inexorable) is
    # pronounced [egz], x- at beginning of word also pronounced [gz], all-
    # other x's pronounced [ks] (including -ex- in lexical, sexy, perplexité,
    # etc.).
    text = rsub(text, rf"([{word_begin}{vowel}]h?)[eæ]x(h?{vowel_c})", r"\1egz\2")
    text = rsub(text, rf"({word_begin_c})in[eæ]xh?(h?{vowel_c})", r"\1egz\2")
    text = rsub(text, rf"({word_begin_c})x", r"\1gz")
    text = rsub(text, r"x", r"ks")

    # Double consonants: eCC treated specially, then CC -> C; do after
    # x -> ks so we handle exciter correctly
    text = rsub(
        text, rf"({word_begin_c})e([mn])\2({vowel_c})", r"\1en_\2\3"
    ) # emmener, ennui
    text = rsub(
        text, rf"({word_begin_c})(h?)[eæ](" + cons_c + r")\3", r"\1\2é\3"
    ) # effacer, essui, errer, henné
    text = rsub(text, rf"({word_begin_c})dess", r"\1déss") # dessécher, dessein, etc.
    text = rsub(text, rf"[eæ]({cons_c})\1", r"è\1") # mett(r)ons, etc.
    text = rsub(text, rf"({cons_c})\1", r"\1")

    # Diphthongs
    # Uppercase is used to avoid the output of one change becoming the input
    # to another; we later lowercase the vowels; î and û converted early;
    # we do this before i/u/ou before vowel -> glide (for e.g. bleuet),
    # and before nasal handling because e.g. ou before n is not converted
    # into a nasal vowel (Bouroundi, Cameroun); au probably too, but there
    # may not be any such words
    text = rsub(text, r"ou", r"U")
    text = rsub(text, r"e?au", r"O")
    text = rsub(text, r"[Ee]u([zt])", r"ø\1")
    text = rsub(text, r"[Ee]uh?([⁀‿])", r"ø\1")  # (s)chleuh has /ø/
    text = rsub(text, r"[Ee][uŭ]", r"œ")
    text = rsub(text, r"[ae]i", r"ɛ")

    # Before implementing nasal vowels, convert nh to n to correctly handle
    # inhérent, anhédonie, bonheur, etc. But preserve enh- to handle
    # enhardir, enharnacher, enhaché, enhoncher, enhotter, enhucher (all
    # with "aspirate h"). Words with "mute h" need respelling with enn-, e.g.
    # enharmonie, enherber.
    text = rsub(text, rf"({word_begin_c})enh", r"\1en_h")
    text = rsub(text, r"nh", r"n")

    # Nasalize vowel + n, m
    # Do before syllabification so we syllabify quatre-vingt-un correctly.
    # We affect (1) n before non-vowel, (2) m before b/p/f (including B/P,
    # which indicate original b/p that are slated to be deleted in words like
    # plomb, champs; f predominantly from original ph, as in symphonie,
    # emphatiser; perhaps we should distinguish original ph from original f,
    # as in occasional words such as Zemfira), (3) -om (nom, dom, pronom,
    # condom, etc.) and (4) -aim/-eim (faim, Reims etc.), (4). We leave alone
    # other m's, including most final m. We do this after diphthongization,
    # which arguably simplifies things somewhat; but we need to handle the
    # 'oi' diphthong down below so we don't run into problems with the 'noi'
    # sequence (otherwise we'd map 'oi' to 'wa' and then nasalize the n
    # because it no longer precedes a vowel).
    nasaltab = {
        "a": "ɑ̃",
        "ä": "ɑ̃",
        "e": "ɑ̃",
        "ë": "ɑ̃",
        "ɛ": "ɛ̃",
        "i": "ɛ̃",
        "ï": "ɛ̃",
        "o": "ɔ̃",
        "ö": "ɔ̃",
        "ø": "œ̃",
        "œ": "œ̃",
        "u": "œ̃",
        "ü": "œ̃",
    }
    def nasalrepl(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 4:
            return "".join([str(match) for match in matches])
        v1, v2, mn, c = matches
        return (f"{v1}{nasaltab[v2]}{c}"
            if mn == "n" or rfind(c, r"[bpBPf]") or (v2 == "o" or v2 == "ɛ") and c == "⁀"
            else f"{v1}{v2}{mn}{c}")
    text = rsub_repeatedly(
        text,
        rf"(.)({vowel_c})([mn])({non_vowel_c})",
        nasalrepl
    )

    # Special hack for maximum, aquarium, circumlunaire, etc.
    text = rsub(text, rf"um({non_vowel_c})", r"ɔm\1")
    # Now remove BP that represent original b/p to be deleted, which we've
    # preserved so far so that we know that preceding m can be nasalized in
    # words like plomb, champs
    text = rsub(text, r"[BP]", r"")

    # Do after nasal handling so 'chinois' works correctly
    text = rsub(text, r"oi", r"wA")

    # Remove silent h (but keep as _ after i/u to prevent glide conversion in
    # nihilisme, jihad, etc.; don't do this after original ou, as souhaite is
    # pronounced /swɛt/).
    # Do after diphthongs to keep vowels apart as in envahir, but do
    # before syllabification so it is ignored in words like hémorrhagie.
    text = rsub(text, r"([iu])h", r"\1_")
    text = rsub(text, r"h", r"")

    # Syllabify
    # (1) Break up VCV as V.CV, and VV as V.V; repeat to handle successive
    #     syllables
    text = rsub_repeatedly(text, rf"({vowel_maybe_nasal_r}{opt_syljoiners_c})({real_cons_c}?{opt_syljoiners_c}{oral_vowel_c})", r"\1.\2")
    # (2) Break up other VCCCV as VC.CCV, and VCCV as VC.CV; repeat to handle successive syllables
    text = rsub_repeatedly(text, rf"({vowel_maybe_nasal_r}{opt_syljoiners_c}{real_cons_c}{opt_syljoiners_c})({real_cons_c}{cons_or_joiner_c}*{oral_vowel_c})", r"\1.\2")

    def resyllabify(text):
        # (3) Resyllabify C.C as .CC for various CC that can form an onset:
        #     Resyllabify C.[lr] as .C[lr] for C = various obstruents;
        #     Resyllabify d.ʒ, C.w, C.ɥ, C.j as .dʒ, .Cw, .Cɥ, .Cj (C.w comes from
        #     written Coi; C.ɥ comes from written Cuill; C.j comes e.g. from
        #     des‿yeux, although most post-consonantal j generated later);
        #     don't resyllabify j.j
        def resyllabify_cc(match: re.Match):
            matches = [m for m in match.groups()]
            if len(matches) != 5:
                return "".join([str(match) for match in matches])
            lparen, c1, j1, j2, c2 = matches
            return (f".{lparen}{c1}{j1}{j2}{c2}"
                    if allow_onset_2(c1, c2)
                    else None)
        text = rsub(text, rf"(\(?)({real_cons_c}{opt_syljoiners_c})\.({opt_syljoiners_c}{real_cons_c})",
            resyllabify_cc)
        # (4) Resyllabify .CC as C.C for CC that can't form an onset (opposite of
        #     the previous step); happens e.g. in ouest-quart
        def resyllabify_cc2(match: re.Match):
            matches = [m for m in match.groups()]
            if len(matches) != 5:
                return "".join([str(match) for match in matches])
            j1, c1, rparen, j2, c2 = matches
            return (f"{j1}{c1}{rparen}.{j2}{c2}"
                if not allow_onset_2(c1, c2)
                    and not (c1 == "s"
                    and rfind(c2, r"^[ptk]$"))
                else None)
        text = rsub(text, rf"\.({opt_syljoiners_c})({real_cons_c})(\)?)({opt_syljoiners_c}{real_cons_c})",
            resyllabify_cc2)
        # (5) Fix up dʒ and tʃ followed by another consonant (management respelt
        #     'manadjment' or similar)
        text = rsub(text, rf"\.([\(]?[dt]{opt_syljoiners_c}[ʒʃ])({opt_syljoiners_c})({real_cons_c})", r"\1.\2\3")
        return text

    text = resyllabify(text)

    # (6) Eliminate diaeresis (note, uï converted early)
    text = rsub(text, r"[äëïöüÿ]", remove_diaeresis_from_vowel)

    # Single vowels
    text = rsub(text, r"â", r"ɑ")
    # Don't do this, too many exceptions
    # text = rsub(text, r"a(\.?)z", r"ɑ\1z")
    text = rsub(text, r"ă", r"a")
    text = rsub(text, r"e\.j", r"ɛ.j") # réveiller
    text = rsub_repeatedly(text, rf"e\.({cons_no_liaison_c}*{vowel_c})", r"ə.\1")
    text = rsub(text, r"e([⁀‿])", r"ə\1")
    text = rsub(text, r"æ\.", r"é.")
    text = rsub(text, r"æ([⁀‿])", r"é\1")
    text = rsub(text, r"[eèêæ]", r"ɛ")
    text = rsub(text, r"é", r"e")
    text = rsub(text, r"o([⁀‿])", r"O\1")
    text = rsub(text, r"o(\.?)z", r"O\1z")
    text = rsub(text, r"[oŏ]", r"ɔ")
    text = rsub(text, r"ô", r"o")
    text = rsub(text, r"u", r"y")

    # Other consonants
    text = rsub(text, r"r", r"ʁ")
    text = rsub(text, r"g", r"ɡ") # Use IPA variant of g

    # (Mostly) final schwa deletions (FIXME, combine with schwa deletions below)
    # 1. Delete all instances of ė
    text = rsub(text, r"\.([^.⁀]+)ė", r"\1")
    # 2. Delete final schwa, only in the last word, not in single-syllable word
    #    (⁀. can occur after a hyphen, e.g. in puis-je)
    text = rsub(text, r"([^⁀])\.([^ə.⁀]+)ə⁀⁀", r"\1\2⁀")
    # 3. Delete final schwa before vowel in the next word, not in a single-
    #    syllable word (croyez-le ou non); the out-of-position \4 looks weird
    #    but the effect is that we preserve the initial period when there's a
    #    hyphen and period after the schwa (con.tre-.a.tta.quer ->
    #    con.tra.tta.quer) but not across a space (con.tre a.tta.quer ->
    #    contr a.tta.quer)
    text = rsub(text, rf"([^⁀])\.([^ə.⁀]+)ə⁀([⁀ \-]*)(\.?)({vowel_c})", r"\1\4\2⁀\3\5")
    # 4. Delete final schwa before vowel in liaison, not in a single-syllable word
    text = rsub(text, rf"([^⁀]\.[^ə.⁀]+)ə‿\.?({vowel_c})", r"\1‿\2")
    # 5. Delete schwa after any vowel (agréerons, soierie)
    text = rsub(text, rf"({vowel_c}).ə", r"\1")
    # 6. Make final schwa optional after two consonants except obstruent + approximant
    #    and [lmn] + ʁ
    def opt_final_schwa(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 3:
            return "".join([str(match) for match in matches])
        a, dot, b = matches
        return f"{a}{dot}{b}{'ə' if rfind(a, r'[bdfɡkpstvzʃʒ]') and rfind(b, r'[mnlʁwj]') else 'ə' if rfind(a, r'[lmn]') and b == 'ʁ' else '(ə)'}⁀"
    text = rsub(text, rf"({cons_c})(\.?)({cons_c})ə⁀", opt_final_schwa)

    #    i/u/ou -> glide before vowel
    #    Do from right to left to handle continuions and étudiions
    #    correctly
    #    Do repeatedly until no more subs (required due to right-to-left
    #    action)
    #    Convert to capital J and W as a signal that we can convert them
    #    back to /i/ and /u/ later on if they end up preceding a schwa or
    #    following two consonants in the same syllable, whereas we don't
    #    do this to j from other sources (y or ill) and w from other
    #    sources (w or oi); will be lowercased later; not necessary to do
    #    something similar to ɥ, which can always be converted back to /y/
    #    because it always originates from /y/.
    i = 0
    while i < 100: # Always ensure to escape the loop instead of using `while True`
        i += 1
        new_text = rsub(text, rf"^(.*)i\.?({vowel_c})", r"\1J\2")
        new_text = rsub(new_text, rf"^(.*)y\.?({vowel_c})", r"\1ɥ\2")
        new_text = rsub(new_text, rf"^(.*)U\.?({vowel_c})", r"\1W\2")
        if new_text == text:
            break
        text = new_text

    # Hack for agréions, pronounced with /j.j/
    text = rsub(text, r"e\.J", r"ej\.J")

    # Glides -> full vowels after two consonants in the same syllable
    # (e.g. fl, tr, etc.), but only glides from original i/u/ou (see above)
    # and not in the sequence 'ui' (e.g. bruit), and only when the second
    # consonant is l or r (not in abstiennent)
    text = rsub(text, rf"({cons_c}[lʁ])J({vowel_c})", r"\1i.j\2")
    text = rsub(text, rf"({cons_c}[lʁ])W({vowel_c})", r"\1u.\2")
    text = rsub(text, rf"({cons_c}[lʁ])ɥ({vowel_no_i_c})", r"\1y.\2")
    # Remove _ that prevents interpretation of letter sequences; do this
    # before deleting internal schwas
    text = rsub(text, r"_", r"")

    # Internal schwa
    # 1. Delete schwa in VCəCV sequence word-internally when neither V is
    #    schwa, except in a few sequences such as ʁəʁ (déchirerez), ɲəʁ
    #    (indignerez), ɲəl (agnelet); use uppercase schwa when not deleting it,
    #    see below; FIXME, we might want to prevent schwa deletion with other
    #    consonant sequences
    def delete_schwa_in_vcxcv(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 4:
            return "".join([str(match) for match in matches])
        v1, c1, c2, v2 = matches
        return (rf"{v1}.{c1}Ə.{c2}{v2}"
                if no_delete_schwa_in_vcvcv_word_internally.get(f"{c1}{c2}")
                else rf"{v1}{c1}.{c2}{v2}")
    text = rsub_repeatedly(text, rf"({vowel_no_schwa_c})\.({real_cons_c})ə\.({real_cons_c})({vowel_no_schwa_c})",
        delete_schwa_in_vcxcv)

    # 2. Delete schwa in VCə.Cʁə, VCə.Clə sequence word-internally
    #    (palefrenier, vilebrequin).
    text = rsub(text, rf"({vowel_no_schwa_c})\.({real_cons_c})ə\.({real_cons_c})([lʁ]ə)", r"\1\2.\3\4")

    # 3. Make optional internal schwa in remaining VCəCV sequences, including
    #    across words, except between certain pairs of consonants (FIXME, needs
    #    to be smarter); needs to happen after /e/ -> /ɛ/ before schwa in next
    #    syllable and after removing ' and _ (or we need to take them into account);
    #    include .* so we go right-to-left, convert to uppercase schwa so
    #    we can handle sequences of schwas and not get stuck if we want to
    #    leave a schwa alone.
    def optional_internal_schwa(match: re.Match):
        matches = [m for m in match.groups()]
        if len(matches) != 6:
            return "".join([str(match) for match in matches])
        v1, c1, sep1, sep2, c2, v2 = matches
        return (rf"{v1}{c1}{sep1}Ə{sep2}{c2}{v2}"
                if no_delete_schwa_in_vcvcv_across_words.get(f"{c1}{c2}")
                else rf"{v1}{c1}{sep1}(Ə){sep2}{c2}{v2}")
        
    text = rsub_repeatedly(text, rf"(.*{vowel_c}{opt_schwajoiners_c})({real_cons_c})({opt_schwajoiners_c})ə({opt_schwajoiners_c})({real_cons_c})({opt_schwajoiners_c}{vowel_c})",
        optional_internal_schwa)

    # Lowercase any uppercase letters (AOUMNJW etc.); they were there to
    # prevent certain later rules from firing
    text = ulower(text)

    # ĕ forces a pronounced schwa
    text = rsub(text, r"ĕ", r"ə")

    # Need to resyllabify again in cases like 'saladerie', where deleting the
    # schwa above caused a 'd.r' boundary that needs to become '.dr'.
    text = resyllabify(text)

    # Rewrite apostrophes as liaison markers
    text = rsub(text, r"'", r"‿")

    # Convert explicit-notation characters to their final result
    text = rsub(text, explicit_substitution_regex, explicit_substitution_to_sound)

    # Remove hyphens
    text = rsub(text, r"\-", "")
    
    # Remove word-boundary markers
    text = rsub(text, r"⁀", "")
    
    return text


def query_pos(text: str):
    url = f"{WEBSITE_URL}/pos"
    data = json.dumps({"text": text}, ensure_ascii=False)
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    rep = requests.post(url, data, headers=headers)
    return json.loads(rep.text)

def get_pos(word: str) -> str:
    """Return the POS of a single word (WARNING: Context will not be taken into account)"""
    _ = query_pos(word)[0]
    return _['pos']

def get_pos_with_context(text: str, word: str) -> str | None:
    """Return the POS of the first occurence of a word within a text, or None if unfound"""
    if not rfind(text, word):
        return None
    tok = query_pos(text)
    for _ in tok:
        pos = _['pos']
        token_text = _['text']
        if token_text == word:
            return pos
    return None # For security but should be useless

def get_tokens_of_pos(text: str, pos: str | list[str], neg: bool = False) -> set[str]:
    """Get the set of all tokens from `text` having POS `pos` (or **not** having if `neg` is True)"""
    tok = query_pos(text)
    if isinstance(pos, str):
        if neg:
            return {_['text'] for _ in tok if _['pos'].lower() != pos.lower()}
        else:
            return {_['text'] for _ in tok if _['pos'].lower() == pos.lower()}
    else:
        if neg:
            return {_['text'] for _ in tok if _['pos'].lower() not in map(lambda x: x.lower(), pos)}
        else:
            return {_['text'] for _ in tok if _['pos'].lower() in map(lambda x: x.lower(), pos)}

def replace_on_pos(text: str, pos: str | list[str], pattern: str, repl, neg = False) -> str:
    """Apply :func:`rsub(word, pattern, repl)` for each `word` of `text` having POS `pos`.
    If `neg`, apply it for each word not having POS `pos`.
    """
    # Using invisible temporary replacement characters
    INV_1 = "\uFFF3"
    INV_2 = "\uFFF4"
    REPL_1 = f" {INV_1} "
    REPL_2 = f" {INV_2} "
    # Hide symbols that prevent good tokenization
    text_cleaned = text
    text_cleaned = rsub(text_cleaned, r"[⁀]", REPL_1)
    text_cleaned = rsub(text_cleaned, r"[‿]", REPL_1)
    tokens = get_tokens_of_pos(text_cleaned, pos, neg)
    # Remove invisible characters from tokens if they matched
    tokens.discard(INV_1)
    tokens.discard(INV_2)
    
    def conditional_replace(match: re.Match):
        word = match.group()
        # Replace words that match the specific POS
        return rsub(word, pattern, repl) if word in tokens else word
    
    # Replace words with the conditional replacement
    text_replaced = rsub(text_cleaned, r"\b\w+\b", conditional_replace)
    # Put back the hidden characters
    text_replaced = rsub(text_replaced, REPL_1, "⁀")
    text_replaced = rsub(text_replaced, REPL_2, "‿")
    return text_replaced

def phoneticize(text: str, standard: Literal['eu', 'ca'] = 'eu') -> str:
    if standard not in ['eu', 'ca']:
        raise ValueError("Wrong standard! Must be either [eu]ropean or [ca]nadian.")
    if standard == 'ca': # TODO - Throw an error for the moment
        raise ValueError("Canadian French is not supported yet. Please choose European French instead.")
    return convert(text)