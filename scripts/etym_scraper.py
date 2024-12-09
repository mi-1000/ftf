import re
import requests
import roman
from bs4 import BeautifulSoup

def extract_dates(word):
    # URL de recherche pour le CNRTL
    url = f"https://www.cnrtl.fr/definition/{word}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête pour le mot '{word}': {e}")
        return None

    # Analyse de la page HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # print(soup)

    # Trouve les balises <b> correspondantes
    start_tag = soup.find("b", string=re.compile(r"^.*Étym?o?l?\. (et Hist\.)?\s*:?.*$", re.IGNORECASE))
    end_tag = soup.find("b", string=re.compile(r"^.*Fréq\. (abs\.)? (litt\.|littér\.)?.*$", re.IGNORECASE))
    
    if not start_tag:
        # print(f"Les balises <b> nécessaires ne sont pas présentes pour le mot '{word}'.")
        section = soup.find("div", attrs={"id": "contentbox"}).text
        section = re.sub(r"<.*>", " ", section)
        if section is None:
            return None
    else:
        # Extrait le texte entre les deux balises
        section = ""
        for element in start_tag.next_elements:
            if element == end_tag:
                break
            section += element.get_text(separator=" ") + " "
    
    # print(section)

    # Extrait les dates (années et siècles)
    date_pattern = re.compile(r"\b(?<!\bp\.\s)(?<!\bp\.)(1[0-9]{3}|20[0-9]{2}|(\d{3}))|((\d{1,2}|[iIvVxX]+)\s*(eme|ème|è|e|ᵉ)\s*((?:s|S)i(è|e)cle)?)\b") # Demande à ChatGPT de t'expliquer ça pcq flemme
    matches = re.findall(date_pattern, section)

    # Convertit les résultats en années
    dates = []
    for match in matches:
        if type(match) == tuple:
            match = match[0]
        if re.match(r"\d{3,4}", match): # Si le match est une date à 3 ou 4 chiffres
            match = int(match)
            dates.append(match) if match >= 842 else None # On ne garde que les dates après 842 (première attestation du français)
        else:
            match = match.lower().replace("ème", "").replace("eme", "").replace("ᵉ", "").replace("e", "").replace("siecle", "").replace("siècle", "").strip() # On uniformise en retirant tout ce qui pourrait polluer l'extraction de la date
            if re.match(re.compile(r"[ivx]+", re.IGNORECASE), match): # Si le match est une date en chiffres romains
                match = roman.fromRoman(match.upper()) * 100 # On convertit les siècles en la première année dudit siècle
                dates.append(match) if match >= 842 else None

    return sorted(dates)

# Exemple d'utilisation avec des mots au pif
words = ["amour", "rabbin", "ordinateur", "zircon", "dinguerie", "de", "un", "tu", "jour", "ignoble", "voiture", "robot", "abalourdissement", "weltanschauung", "ab hoc et ab hac", "souffrance", "incongru", "désopilant", "néologisme", "acupuncture"]

for word in words:
    dates = extract_dates(word)
    if dates:
        print(f"Dates pour '{word}': {dates}")
    else:
        print(f"Aucune date trouvée pour '{word}'.")
