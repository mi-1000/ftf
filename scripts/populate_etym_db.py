import locale
import requests
import os

import mysql.connector

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mysql.connector import Error

from typing import List, Tuple

from etym_scraper import extract_dates


locale.setlocale(locale.LC_COLLATE, 'fr_FR.UTF-8')

load_dotenv()

def get_links(letter: str, index: int) -> List[Tuple[str, int | None]]:
    """Returns all words starting with a given letter and registered at the given index on CNRTL.

    Args:
        letter (str): The initial letter of queried words
        index (int): The index of the page ()

    Returns:
        List[Tuple[str, int | None]]: A list of tuples of (word, date of first attestation if found else None)
    """
    url = f"https://www.cnrtl.fr/portailindex/LEXI/TLFI/{letter}/{80 * index}"
    response = requests.get(url)

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
                print(f"Parsing word {word} from {url}.")
                dates = extract_dates(word)
                try:
                    if dates is None: # In case of HTTP error
                        raise IndexError
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

letters = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

try:
    connection = mysql.connector.connect(**db_config)
    
    if connection.is_connected():
        print("Connexion réussie.")
        cursor = connection.cursor()
        for letter in letters:
            i = 0
            while True:
                unsorted_links = get_links(letter, i)
                if not unsorted_links:
                    break
                links = sorted(unsorted_links, key=lambda x: locale.strxfrm(x[0].lower()))
                for entry in links:
                    query = "INSERT INTO `etymology`(`word`, `date`) VALUES (%s, %s)"
                    cursor.execute(query, (entry[0], entry[1]))
                    connection.commit()
                    print(f"[INFO] Added word {entry[0]} ({entry[1]}) to database.")
                i += 1

except Error as e:
    print(f"Erreur : {e}")
finally:
    # Close resources
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connexion fermée.")