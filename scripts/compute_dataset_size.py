from os import listdir
from os.path import isfile, join

path = "data/raw/data_latin"

files = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f.startswith("pair_Vulgate_FreSegond_") and f.endswith('_la.txt')]

chars = 0
words = 0
nb_files = len(files)

for file in files:
    with open(file, 'r') as f:
        text = f.read()
        chars += len(text)
        words += len(text.split())

print(f"Total: {nb_files} files - {words} words - {chars} characters")