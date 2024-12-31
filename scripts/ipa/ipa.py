from typing import Literal

from ipa_grc import phoneticize as phon_grc
from ipa_la import phoneticize as phon_la

LATIN_PERIODS = ["eccl", "vul", "clas"]
GREEK_PERIODS = ["cla", "koi1", "koi2", "byz1", "byz2"]

def phoneticize(text: str, lang: Literal["la", "grc", "fro"], period: Literal["eccl", "vul", "clas", "cla", "koi1", "koi2", "byz1", "byz2"]) -> str:
    if lang == "la":
        return phon_la(text, period)
    elif lang == "grc":
        return phon_grc(text, period)
    else: # lang == "fro"
        pass # TODO