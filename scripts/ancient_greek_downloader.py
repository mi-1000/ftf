import requests
from bs4 import BeautifulSoup

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

# Afficher les hrefs récupérés
for href in hrefs:
    print(f"{base_url}/{href}/lecture/default.htm")
