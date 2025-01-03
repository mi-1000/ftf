from typing import Literal

from .ipa_fr import phoneticize as phon_fr
from .ipa_grc import phoneticize as phon_grc
from .ipa_la import phoneticize as phon_la

FRENCH_PERIODS = ["eu", "ca"]
GREEK_PERIODS = ["cla", "koi1", "koi2", "byz1", "byz2"]
LATIN_PERIODS = ["eccl", "vul", "clas"]
OLD_FRENCH_PERIODS = ["ear", "lat"]

def phoneticize(text: str, lang: Literal["fr", "la", "grc", "fro"], period: Literal["eu", "ca", "eccl", "vul", "clas", "cla", "koi1", "koi2", "byz1", "byz2", "ear", "lat"]) -> str:
    """Phoneticize a Latin, Ancient Greek or Old French text into IPA.

    Args:
        text (str): The text to convert
        lang (Literal[&quot;la&quot;, &quot;grc&quot;, &quot;fro&quot;]): The language of the text
        period (Literal[&quot;eu&quot;, &quot;ca&quot;, &quot;eccl&quot;, &quot;vul&quot;, &quot;clas&quot;, &quot;cla&quot;, &quot;koi1&quot;, &quot;koi2&quot;, &quot;byz1&quot;, &quot;byz2&quot;, &quot;ear&quot;, &quot;lat&quot;,]): The period/region of the language

    Raises:
        ValueError: Unauthorized arguments for language or period, or missing argument(s)

    Returns:
        str: The corresponding IPA string
    """
    if not text or not lang or not period:
        raise ValueError("Argument missing in phoneticize(text, lang, period).")
    if lang not in ["fr", "la", "grc", "fro"]:
        raise ValueError("Incorrect parameter for lang. Authorized values are 'grc', 'la', 'fro'.")
    if lang == "la":
        if period not in LATIN_PERIODS:
            raise ValueError("Incorrect Latin period. Authorized values are 'clas', 'eccl', 'vul'.")
        return phon_la(text, period)
    elif lang == "grc":
        if period not in GREEK_PERIODS:
            raise ValueError("Incorrect Ancient Greek period. Authorized values are 'byz1', 'byz2', 'cla', 'koi1', 'koi2'.")
        return phon_grc(text, period)
    elif lang == "fro":
        if period not in OLD_FRENCH_PERIODS:
            raise ValueError("Incorrect Old French period. Authorized values are 'ear', 'lat'.")
        raise ValueError("Old French is not supported yet.") # TODO
    elif lang == "fr":
        if period not in FRENCH_PERIODS:
            raise ValueError("Incorrect French standard. Authorized values are 'eu', 'ca'.")
        return phon_fr(text, period)
    else: # This should not happen
        raise ValueError("Parameter lang is not valid. Authorized languages are 'fr', 'fro', 'grc', 'la'.")