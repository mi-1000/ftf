import cltk
import nltk

def normalizer(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        words = nltk.tokenize(line)
        normalize_words = cltk.normalize_fr(words)

        line = "".join(normalize_words)

    print(lines[:20])

def main():
    file = "chanson_de_rolland_fro"
