import json

import os
import requests
import urllib.request as req

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from typing import List

def get_metadata_from_id(id: str) -> str:
    """Retrieves XML-formatted metadata from a file through its id

    Args:
        id (str): The id of the file

    Returns:
        str: The XML metadata, leaving file name as `*`
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
    
    return f'<item link="https://nakala.fr/{id}" language="old-french" filename="*" date="{date}" place="" />'

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

def download_all_files(collection_id: str = "10.34847/nkl.1279lie9", output_folder: str = "data/data_old_french"):
    """Downloads all files from a given collection to the folder of your choice and saves metadata to a temporary XML file (`sources_tmp.xml`) that you can then copy and paste

    Args:
        collection_id (str, optional): The id of the collection. Defaults to "10.34847/nkl.1279lie9".
        output_folder (str, optional): The output folder for files. Defaults to "data/data_old_french".
    """
    with open('sources_tmp.xml', 'w') as f:
        sources = ""
        ids = get_file_identifiers_from_collection(collection_id)
        for id in ids:
            url = get_download_link_from_id(id)
            with req.urlopen(url) as response:
                content_disposition = response.headers.get('Content-Disposition')
                if content_disposition and 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                else:
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path)
            output_location = f"{output_folder}/{filename}"
            metadata = get_metadata_from_id(id).replace('*', output_location)
            sources += metadata + '\n'
            req.urlretrieve(url, output_location)
        f.write(sources)

def main():
    download_all_files()

if __name__ == '__main__':
    main()