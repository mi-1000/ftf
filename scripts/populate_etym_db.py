import requests
import mysql.connector
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from etym_scraper import extract_dates
url = "https://www.cnrtl.fr/portailindex/LEXI/TLFI/A/0"

load_dotenv()

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = soup.findAll("a")
    words = []
    for link in links:
        href = link.get("href")
        if href.startswith('/definition'):
            word = href.replace('/definition/', '')
            words.append((word, extract_dates(word)[0])) if href != '/definition/' else None
    print(words)
       


words = [item[0] for item in words]
dates = [item[1] for item in words]
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USERNAME"), 
    password=os.getenv("DB_PASSWORD"), 
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()
cursor.execute("")
for word, date in zip(words, dates):
     cursor.execute((word, date))
db.commit()
cursor.close()
db.close()

print("done!")