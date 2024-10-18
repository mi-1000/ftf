import requests
import re
from bs4 import BeautifulSoup

# base_url = "http://mercure.fltr.ucl.ac.be/Hodoi/concordances"
# # URL de la page
# url = f"{base_url}/intro.htm"

# # Récupérer le contenu de la page
# response = requests.get(url)
# response.raise_for_status()  # Vérifie si la requête a réussi

# # Parser le contenu HTML
# soup = BeautifulSoup(response.text, 'html.parser')

# # Trouver tous les attributs href des balises <a>
# hrefs = []
# for a in soup.find_all('a', href=True):
#     href = a['href']
#     if not href.startswith('mailto:') and not href.startswith('#') and not href.startswith('http'):
#         hrefs.append(href)
# print(len(hrefs))

# hrefsfinal = []
# # Afficher les hrefs récupérés
# for href in hrefs:
#     url=f"{base_url}/{href}/lecture/default.htm"
#     # Récupérer le contenu de la page
#     try:
#         # Attempt to retrieve the page
#         response = requests.get(url)
#         response.raise_for_status()  # This will raise an HTTPError for bad responses
#     except requests.exceptions.RequestException as e:
#         # Log and skip the URL if an error occurs
#         print(f"Failed to retrieve {url}: {e}")
#         continue  # Skip to the next URL
#     else:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         for a in soup.find_all('a', href=True):
#             href2 = a['href']
#             if href2[0].isdigit():
#                 full_url = f"{base_url}/{href}/lecture/{href2}"
#                 hrefsfinal.append(full_url)

# print(len(hrefsfinal))

# texts = []

# for href in hrefsfinal:
#     url=f"{hrefsfinal}"
#     # Récupérer le contenu de la page
#     try:
#         # Attempt to retrieve the page
#         response = requests.get(url)
#         response.raise_for_status()  # This will raise an HTTPError for bad responses
#     except requests.exceptions.RequestException as e:
#         # Log and skip the URL if an error occurs
#         print(f"Failed to retrieve {url}: {e}")
#         continue  # Skip to the next URL
#     else:
#        for f in soup.find_all('font', attrs={"size": "+1","color":"red",}):
#         # Extract text from the tag
#         title = f.get_text()

#        for f in soup.find_all('font', attrs={"size": "-1",}):
#         # Extract text from the tag
#         font_text = f.get_text()
#         texts.append(font_text.strip().replace(f"\r",""))  # Strip extra whitespace

#         greek_text = texts[0::2]
#         french_text = texts[1::2]

# print(greek_text,"\n",french_text)






url = "https://mercure.fltr.ucl.ac.be/Hodoi/concordances/Achilles_Tatius_leu01/lecture/1.htm"

response = requests.get(url)
response.raise_for_status()
response.encoding = response.apparent_encoding 
soup = BeautifulSoup(response.text, 'html.parser')

# for f in soup.find_all('font', attrs={"size": "-1", "face": "palatino linotype"}):
title = []

for f in soup.find_all('font', attrs={"size": "+1","color":"red",}):
        # Extract text from the tag
        title.append(f.get_text().strip())

# Find all <font> tags with specific attributes
for f in soup.find_all('font', attrs={"size": "-1",}):
        text = []
        # Extract text from the tag
        font_text = f.get_text()
        text.append(font_text.strip().replace(f"\r",""))  # Strip extra whitespace
        print(text[0])
        greek_text = text[0::2]
        # print(greek_text)
        french_text = text[1::2]

        with open(f"{title[0]}_greek.txt", "a", encoding='utf-8') as file:

                for text in greek_text:
                        cleaned_text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
                        lines = cleaned_text.split('\n')
                        for line in lines:
                                file.write(line+"\n")

# print(greek_text,"\n",french_text)