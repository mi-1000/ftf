from bs4 import BeautifulSoup

from os import listdir
from os.path import isfile, join

_WIDTH = 60

def compute_size_bible_latin():
    path = "data/raw/data_latin"

    files = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f.startswith("pair_Vulgate_FreSegond_")]
    files_fr = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f.startswith("pair_Vulgate_FreSegond_") and f.endswith('_fr.txt')]
    files_la = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f.startswith("pair_Vulgate_FreSegond_") and f.endswith('_la.txt')]

    chars = 0; chars_fr = 0; chars_la = 0
    words = 0; words_fr = 0; words_la = 0

    nb_files = len(files); nb_files_fr = len(files_fr); nb_files_la = len(files_la)

    for file in files:
        with open(file, 'r') as f:
            text = f.read()
            chars += len(text)
            words += len(text.split())
    
    for file in files_fr:
        with open(file, 'r') as f:
            text = f.read()
            chars_fr += len(text)
            words_fr += len(text.split())
            
    for file in files_la:
        with open(file, 'r') as f:
            text = f.read()
            chars_la += len(text)
            words_la += len(text.split())

    print(" Bible: ".center(_WIDTH, '='))
    print(f" Total: {nb_files} files - {words} words - {chars} characters ".center(_WIDTH, '='))
    print(f" French: {nb_files_fr} files - {words_fr} words - {chars_fr} characters ".center(_WIDTH, '='))
    print(f" Latin: {nb_files_la} files - {words_la} words - {chars_la} characters ".center(_WIDTH, '='))
    print("".center(_WIDTH, '=') + '\n')

def compute_size_bfm_old_french():
    path = "data/raw/data_old_french"

    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    chars = 0
    words = 0

    nb_files = len(files)

    for file in files:
        with open(file, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'xml')
        w_tags = soup.find_all('w')
        for word in w_tags:
            words += 1
            chars += len(word.text)

    print(" BFM: ".center(_WIDTH, '='))
    print(f" Total: {nb_files} files - {words} words - {chars} characters ".center(_WIDTH, '='))
    print("".center(_WIDTH, '=') + '\n')

if __name__ == "__main__":
    compute_size_bible_latin()
    compute_size_bfm_old_french()