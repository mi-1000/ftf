import re
import requests
import roman
import time
from bs4 import BeautifulSoup

def extract_dates(word):
    url = f"https://www.cnrtl.fr/definition/{word}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête pour le mot '{word}': {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # print(soup)

    # On cherche la section étymologie de la page
    start_tag = soup.find("b", string=re.compile(r"^.*Étym?o?l?\. (et Hist\.)?\s*:?.*$", re.IGNORECASE))
    end_tag = soup.find("b", string=re.compile(r"^.*Fréq\. (abs\.)? (litt\.|littér\.)?.*$", re.IGNORECASE))
    
    if not start_tag: # Si on ne trouve pas la section étymologie, on récupère toute la page
        # print(f"Les balises <b> nécessaires ne sont pas présentes pour le mot '{word}'.")
        section = soup.find("div", attrs={"id": "contentbox"}).text
        section = re.sub(r"<.*>", " ", section) # On retire les tags HTML
        if section is None:
            return None # Si vraiment on ne trouve rien, on retourne None
    else:
        # Extrait le texte entre les deux balises
        section = ""
        for element in start_tag.next_elements:
            if element == end_tag:
                break
            section += element.get_text(separator=" ") + " "
    section = re.sub(r"(pp?|pages?)\.+\s*\d+(\s*[,;\-\/]\s*\d+)*", "", section) # On retire les numéros de pages qui risquent d'être confondus avec des dates
    
    # print(section)

    # On extrait les dates (années et siècles)
    date_pattern = re.compile(r"\b(?<!\bp\.\s)(?<!\bp\.)(1[0-9]{3}|20[0-9]{2}|(\d{3}))|((\d{1,2}|[iIvVxX]+)\s*(eme|ème|è|e|ᵉ)\s*(?:s|S)(i(?:è|e)cle)?)\b") # Demande à ChatGPT de t'expliquer ça pcq flemme
    matches = re.findall(date_pattern, section)

    # On convertit les résultats en années et les ajoute à une liste
    dates = []
    for match in matches:
        if type(match) == tuple:
            match = match[0] # On garde le groupe de capture global
        if re.match(r"\d{3,4}", match): # Si le match est une date à 3 ou 4 chiffres
            match = int(match)
            dates.append(match) if match >= 842 else None # On ne garde que les dates après 842 (première attestation du français)
        else:
            match = match.lower().replace("ème", "").replace("eme", "").replace("ᵉ", "").replace("e", "").replace("siecle", "").replace("siècle", "").strip() # On uniformise en retirant tout ce qui pourrait polluer l'extraction de la date
            if re.match(re.compile(r"[ivx]+", re.IGNORECASE), match): # Si le match est une date en chiffres romains
                match = roman.fromRoman(match.upper()) * 100 # On convertit les siècles en la première année dudit siècle
                dates.append(match) if match >= 842 else None
    if dates.count(2012) >= 3:
        for i in range(3):
            dates.remove(2012) # On retire les occurences de 2012 qui correspondent au copyright du site

    return sorted(dates)

# Exemple d'utilisation avec des mots au pif
words = ["téléphone", "amour", "rabbin", "ordinateur", "zircon", "il", "lui", "elle", "dinguerie", "de", "un", "tu", "jour", "ignoble", "voiture", "robot", "abalourdissement", "weltanschauung", "ab hoc et ab hac", "souffrance", "incongru", "désopilant", "néologisme", "acupuncture", "constitution", "paganisme", "fenêtre", "parapluie", "avion"]

if __name__ == "__main__":
    timestamp_init = time.time()
    for word in words:
        dates = extract_dates(word)
        if dates:
            print(f"Dates pour '{word}': {dates}")
        else:
            print(f"Aucune date trouvée pour '{word}'.")
    total_time = time.time() - timestamp_init
    print(f"Une requête dure en moyenne {total_time / len(words) * 1000} ms.")