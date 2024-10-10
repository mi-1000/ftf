from bs4 import BeautifulSoup

from os import listdir
from os.path import isfile, join

import xml.etree.cElementTree as ET

_WIDTH = 66

def compute_size_bible_latin():
    path = "data/raw/data_latin"

    files_fr = [
        join(path, f)
        for f in listdir(path)
        if isfile(join(path, f))
        and f.startswith("pair_Vulgate_FreSegond_")
        and f.endswith("_fr.txt")
    ]
    files_la = [
        join(path, f)
        for f in listdir(path)
        if isfile(join(path, f))
        and f.startswith("pair_Vulgate_FreSegond_")
        and f.endswith("_la.txt")
    ]

    chars_fr = 0; chars_la = 0
    words_fr = 0; words_la = 0

    nb_files_fr = len(files_fr); nb_files_la = len(files_la)

    for i, file in enumerate(files_fr):
        print(f"Bible - French: {i + 1} / {len(files_fr)}")
        with open(file, 'r') as f:
            text = f.read()
            chars_fr += len(text)
            words_fr += len(text.split())

    for i, file in enumerate(files_la):
        print(f"Bible - Latin: {i + 1} / {len(files_la)}")
        with open(file, 'r') as f:
            text = f.read()
            chars_la += len(text)
            words_la += len(text.split())

    res = ''
    res += " Bible: ".center(_WIDTH, '=') + '\n'
    res += f" Total: {nb_files_fr + nb_files_la} files - {words_fr + words_la} words - {chars_fr + chars_la} characters ".center(_WIDTH, '=') + '\n'
    res += f" French: {nb_files_fr} files - {words_fr} words - {chars_fr} characters ".center(_WIDTH, '=') + '\n'
    res += f" Latin: {nb_files_la} files - {words_la} words - {chars_la} characters ".center(_WIDTH, '=') + '\n'
    res += "".center(_WIDTH, '=') + '\n\n'
    return res

def compute_size_bfm_old_french():

    tree = ET.parse('sources/sources.xml')
    root = tree.getroot()

    files = [
        item.get('filename') 
        for item in root.findall('item')
        if item.get('link', '').startswith('https://nakala.fr')
    ]

    chars = 0
    words = 0

    nb_files = len(files)

    for i, file in enumerate(files):
        print(f"BFM: {i + 1} / {len(files)}")
        with open(file, 'r', encoding="utf-8") as file:
            content = file.read()
        soup = BeautifulSoup(content, "xml")
        w_tags = soup.find_all("w")
        for word in w_tags:
            words += 1
            chars += len(word.text)

    res = ''
    res += " BFM: ".center(_WIDTH, '=') + '\n'
    res += f" Total: {nb_files} files - {words} words - {chars} characters ".center(_WIDTH, '=') + '\n'
    res += "".center(_WIDTH, '=') + '\n\n'
    return res

def compute_size_frantext_old_and_middle_french():
    tree = ET.parse('sources/sources.xml')
    root = tree.getroot()
    files_old = [item.get('filename') 
        for item in root.findall('item')
        if item.get('link', '').startswith('https://www.frantext.fr')
        and item.get('language') == 'old-french'
    ]
    files_middle = [item.get('filename') 
        for item in root.findall('item')
        if item.get('link', '').startswith('https://www.frantext.fr')
        and item.get('language') == 'middle-french'
    ]

    chars_old = 0; chars_middle = 0
    words_old = 0; words_middle = 0

    nb_files_old = len(files_old); nb_files_middle = len(files_middle)

    for i, file in enumerate(files_old):
        print(f"Frantext - Old French: {i + 1} / {len(files_old)}")
        with open(file, 'r', encoding="utf-8") as file:
            content = file.read()
        soup = BeautifulSoup(content, "xml")
        w_tags = soup.find_all("x:wf")
        for elem in w_tags:
            word = elem.get("word")
            words_old += 1
            chars_old += len(word)

    for i, file in enumerate(files_middle):
        print(f"Frantext - Middle French: {i + 1} / {len(files_middle)}")
        with open(file, 'r', encoding="utf-8") as file:
            content = file.read()
        soup = BeautifulSoup(content, "xml")
        w_tags = soup.find_all("x:wf")
        for elem in w_tags:
            word = elem.get("word")
            words_middle += 1
            chars_middle += len(word)

    res = ''
    res += " Frantext: ".center(_WIDTH, '=') + '\n'
    res += f" Total: {nb_files_old + nb_files_middle} files - {words_old + words_middle} words - {chars_old + chars_middle} characters ".center(_WIDTH, '=') + '\n'
    res += f" Old French: {nb_files_old} files - {words_old} words - {chars_old} characters ".center(_WIDTH, '=') + '\n'
    res += f" Middle French: {nb_files_middle} files - {words_middle} words - {chars_middle} characters ".center(_WIDTH, '=') + '\n'
    res += "".center(_WIDTH, '=') + '\n'
    return res

if __name__ == "__main__":
    bible = compute_size_bible_latin()
    bfm = compute_size_bfm_old_french()
    frantext = compute_size_frantext_old_and_middle_french()
    print(bible, bfm, frantext, sep='\n')