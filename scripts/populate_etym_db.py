import requests
import mysql.connector
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mysql.connector import Error
from etym_scraper import extract_dates

load_dotenv()

def get_links(letter: str, index: int):
    response = requests.get(f"https://www.cnrtl.fr/portailindex/LEXI/TLFI/{letter}/{80 * index}")

    if not response.status_code == 200:
        print(f"HTTP Error {response.status_code}")
        response.raise_for_status()
        exit(1)

    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.findAll("a")
    words = []
    for link in links:
        href = str(link.get("href"))
        if href.startswith('/definition'):
            word = href.replace('/definition/', '')
            if href != '/definition/':
                dates = extract_dates(word)
                try:
                    date = dates.pop(0)
                    words.append((word, date))
                except IndexError: # If no date has been found
                    words.append((word, None))
    return words

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
letters = ["W", "Y", "Z"]

for letter in letters:
    next_letter = False
    i = 0
    while not next_letter:
        links = get_links(letter, i)
        print(letter, i, links)
        if not links:
            next_letter = True
            break
        i += 1

# try:
#     connection = mysql.connector.connect(**db_config)
    
#     if connection.is_connected():
#         print("Connexion réussie.")
#         cursor = connection.cursor()
#         for word in words:
#             query = "INSERT INTO `etymology`(`word`, `date`) VALUES (%s, %s)"
#             cursor.execute(query, (word[0], word[1]))
#             connection.commit()
#         # results = cursor.fetchall()
#         # for row in results:
#         #     print(row)

# except Error as e:
#     print(f"Erreur : {e}")
# finally:
#     # Close resources
#     if 'cursor' in locals() and cursor:
#         cursor.close()
#     if 'connection' in locals() and connection.is_connected():
#         connection.close()
#         print("Connexion fermée.")