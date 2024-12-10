import cltk
import nltk
import os

nltk.download('punkt_tab')

def normalizer(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        words = nltk.tokenize.word_tokenize(line)
        normalize_words = cltk.fro.normalize_fr(words)

        line = "".join(normalize_words)

    print(lines[:20])

def main():
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chanson_de_roland_fro.txt")
    normalizer(file)

if __name__ == "__main__":
    main()