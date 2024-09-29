import json

import requests

from bs4 import BeautifulSoup
from urllib.request import urlretrieve

from typing import List


def get_metadata_from_id(id: str) -> str:
    """Retrieves XML-formatted metadata from a file through its id

    Args:
        id (str): The id of the file

    Returns:
        str: The XML metadata
    """
    url = f"https://api.nakala.fr/datas/{id}/metadatas"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml', from_encoding="UTF-8")
    data_date = json.loads(soup.text)[1]['value']
    if data_date and type(data_date) == str:
        if data_date.startswith("0"):
            data_date = data_date[1:]
        date = data_date.split('-')[0]
    else:
        date = ""
    
    print(f'<item link="https://nakala.fr/{id}" language="old-french" filename="data/data_old_french/*" date="{date}" place="" />')
    return ''

def get_download_link_from_id(id: str) -> str | None:
    """Retrieves the download link of a file from its identifier on `https://nakala.fr`

    Args:
        id (str): The identifier of the file

    Returns:
        str | None: The download link of the file, or None if unfound
    """
    response = requests.get(f"https://nakala.fr/{id}")
    soup = BeautifulSoup(response.content, 'html.parser')

    button = soup.find('button', attrs={'data-clipboard-text': lambda value: value and value.startswith('https://api.nakala.fr/data')})

    if button:
        download_link = button['data-clipboard-text']
        return download_link
    return None

def get_file_identifiers_from_collection(collection: str) -> List[str]:
    """Retrieves all file identifiers from a given collection on `https://nakala.fr`

    Args:
        collection (str): The DOI id of the collection

    Returns:
        List[str]: The list of file identifiers from the given collection
    """
    identifiers = []
    for i in range(1, 10): # 9 pages * 25 files per page
        response = requests.get(f"https://api.nakala.fr/collections/{collection}/datas?page={i}&limit=25")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml', from_encoding="UTF-8")
        data = json.loads(soup.text)
        for i, key in enumerate(data['data']):
            identifiers.append(data['data'][i]['identifier'])
    return identifiers

def main():
    bfm_doi = "10.34847/nkl.1279lie9"
    ids = get_file_identifiers_from_collection(bfm_doi)
    links = []
    for id in ids:
        # links.append(get_download_link_from_id(id))
        # print(links)
        print(get_metadata_from_id(id))

if __name__ == '__main__':
    main()