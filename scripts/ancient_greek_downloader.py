import requests
import re
from bs4 import BeautifulSoup

def writetext(texts, file):
    for text in texts:
        cleaned_text = re.sub(r'\[.*?\]|\(.*?\)', '', text)  # Remove [..] and (..)
        cleaned_text = re.sub(r'(?<=\n)\s+', '', cleaned_text)
        file.write(cleaned_text + "\n\n")

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


base_url = "http://mercure.fltr.ucl.ac.be/Hodoi/concordances"
# URL de la page
url = f"{base_url}/intro.htm"

# Récupérer le contenu de la page
response = requests.get(url)
response.raise_for_status()  # Vérifie si la requête a réussi

# Parser le contenu HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Trouver tous les attributs href des balises <a>
hrefs = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if not href.startswith('mailto:') and not href.startswith('#') and not href.startswith('http'):
        hrefs.append(href)
# print(len(hrefs))

hrefsfinal = []
# Afficher les hrefs récupérés
for href in hrefs:
    url=f"{base_url}/{href}/lecture/default.htm"
    # Récupérer le contenu de la page
    try:
        # Attempt to retrieve the page
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        # Log and skip the URL if an error occurs
        print(f"Failed to retrieve {url}: {e}")
        continue  # Skip to the next URL
    else:
        soup = BeautifulSoup(response.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            href2 = a['href']
            if href2[0].isdigit():
                full_url = f"{base_url}/{href}/lecture/{href2}"
                hrefsfinal.append(full_url)

total = len(hrefsfinal)
print(total)
texts = []

# Inside your loop where you write files:
for index, href in enumerate(hrefsfinal):
    print(f"{index + 1}/{total}")  # Print progress as X/Y
    url = href  # Correct assignment, now only the current href is used

    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        continue  # Skip to the next URL
    else:
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title
        title = []
        for f in soup.find_all('font', attrs={"size": "+1", "color": "red"}):
            title.append(f.get_text().strip().replace(" ", "_"))

        if title:
            safe_title = sanitize_filename(title[0])  # Sanitize the title

            # Collect all the text
            text = []
            for f in soup.find_all('font', attrs={"size": "-1"}):
                font_text = f.get_text()
                text.append(font_text.strip().replace(f"\r", ""))  # Strip extra whitespace

            # Split the text into Greek and French parts
            greek_text = text[0::2]
            french_text = text[1::2]

            # Write Greek text to file
            with open(f"C:/Bureau/Master/S7/project/greek_text/{safe_title}_greek.txt", "w", encoding='utf-8') as file:
                writetext(greek_text, file)

            # Write French text to file
            with open(f"C:/Bureau/Master/S7/project/greek_text/{safe_title}_french.txt", "w", encoding='utf-8') as file:
                writetext(french_text, file)



# url = "https://mercure.fltr.ucl.ac.be/Hodoi/concordances/Achilles_Tatius_leu01/lecture/1.htm"

# response = requests.get(url)
# response.raise_for_status()
# response.encoding = response.apparent_encoding
# soup = BeautifulSoup(response.text, 'html.parser')

# # Extract the title
# title = []
# for f in soup.find_all('font', attrs={"size": "+1", "color": "red"}):
#     title.append(f.get_text().strip().replace(" ", "_"))

# # Collect all the text
# text = []
# for f in soup.find_all('font', attrs={"size": "-1"}):
#     font_text = f.get_text()
#     text.append(font_text.strip().replace(f"\r", ""))  # Strip extra whitespace

# # Split the text into Greek and French parts
# greek_text = text[0::2]
# french_text = text[1::2]

# # Write Greek text to file
# with open(f"C:/Bureau/Master/S7/project/greek_text/{title[0]}_greek.txt", "w", encoding='utf-8') as file:
#     writetext(greek_text, file)

# # Write French text to file
# with open(f"C:/Bureau/Master/S7/project/greek_text/{title[0]}_french.txt", "w", encoding='utf-8') as file:
#     writetext(french_text, file)
