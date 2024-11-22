# import asyncio
# import requests
# from bs4 import BeautifulSoup
# from crawl4ai import AsyncWebCrawler
# from typing import List, Dict

# async def fetch_text_links(url: str) -> List[str]:
#     """Fetches all text links from a given author's page.

#     Args:
#         url (str): The URL of the author's page to crawl.

#     Returns:
#         List[str]: A list of URLs for the texts found on the page.
#     """
#     res = []
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:  # status ok
#         soup = BeautifulSoup(response.content, "html.parser")
#         links = soup.find_all('a')  # get all <a> tags

#         for link in links:
#             href = link.get('href')
#             if href and href.startswith("/loc"):  # Match text links
#                 full_url = f"https://latin.packhum.org{href}"
#                 res.append(full_url)
#     else:
#         print(f"Error: Received status code {response.status_code} for {url}")
#     return res

# async def crawl_authors(base_url: str = "https://latin.packhum.org/browse") -> List[str]:
#     """Crawls the given base page and returns a list of author URLs.

#     Args:
#         base_url (str): The URL of the base page to crawl.

#     Returns:
#         List[str]: A list of URLs for the authors found on the page.
#     """
#     res = []
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
#     }
#     response = requests.get(base_url, headers=headers)

#     if response.status_code == 200:  # status ok
#         soup = BeautifulSoup(response.content, "html.parser")
#         links = soup.find_all('a')  # get all <a> tags

#         for link in links:
#             href = link.get('href')
#             if href and href.startswith("/author/"):  # Match author links
#                 full_url = f"https://latin.packhum.org{href}"
#                 res.append(full_url)
#     else:
#         print(f"Error: Received status code {response.status_code}")
#     return res

# async def main():
#     # Step 1: Get all author links from the base page
#     author_links = await crawl_authors()
#     print(f"Found {len(author_links)} author links.")

#     # Step 2: For each author link, fetch text links
#     all_text_links: Dict[str, List[str]] = {}
#     for author_link in author_links:
#         print(f"Crawling author page: {author_link}")
#         text_links = await fetch_text_links(author_link)
#         all_text_links[author_link] = text_links
#         print(f"Found {len(text_links)} text links on {author_link}")

#     # Print the dictionary of all collected text links
#     for author, links in all_text_links.items():
#         print(f"\nText links for {author}:")
#         try:
#             async with AsyncWebCrawler(verbose=True) as crawler:
#                 for link in links:
#                     result = await crawler.arun(url=link)
#                     print(result.markdown)
#         except Exception:
#             pass

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio 
import requests
from bs4 import BeautifulSoup
from typing import List
import unicodedata
import os
import re

def remove_diacritics(input_str: str) -> str:
    """Removes diacritics from a given string."""
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if unicodedata.category(c) != 'Mn')

def contains_numbers(text: str) -> bool:
    """Returns True if the text contains any numbers."""
    return any(char.isdigit() for char in text)

def is_only_punctuation_or_numbers(text: str) -> bool:
    """Returns True if the text contains only punctuation and/or numbers."""
    return re.fullmatch(r'^[\d\W_]+$', text) is not None

def is_line_starting_with_non(text: str) -> bool:
    """Returns True if the line starts with 'Non.'."""
    return text.startswith("Non.")

async def fetch_and_save_text(url: str, author_name: str):
    """Fetches the text content from a given URL and saves it to .txt files with the title as the filename."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:  # Status ok
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <td> elements
        cells = soup.find_all("td")
        content = []
        current_title = None

        for cell in cells:
            cell_text = cell.get_text(strip=True)

            # Ignore cells that contain numbers, punctuation, or that start with 'Non.'
            if contains_numbers(cell_text) or is_only_punctuation_or_numbers(cell_text):
                continue
            
            # Check if the cell contains uppercase text and acts as a new title
            if cell_text.isupper():
                if current_title and content:
                    # Save the previous content to a file
                    save_text_to_file(current_title, content, author_name)
                
                # Start a new section
                current_title = cell_text
                content = []
            else:
                content.append(cell_text)

        # Save the last section if any
        if current_title and content:
            save_text_to_file(current_title, content, author_name)

    else:
        print(f"Error: Received status code {response.status_code} for {url}")

def save_text_to_file(title: str, content: List[str], author_name: str):
    """Saves the content to a file with the title as the filename."""
    directory = "texts"  
    os.makedirs(directory, exist_ok=True)
    
    # Clean the title and filename
    clean_title = remove_diacritics(title).replace(" ", "")
    clean_author = remove_diacritics(author_name).replace(" ", "")
    filename = os.path.join(directory, f"{clean_author}_{clean_title}.txt")
    
    # Join the content lines
    text_content = "\n".join(content).strip()

    # Remove the first line if there's more than one line
    if text_content:
        text_lines = text_content.splitlines()
        if len(text_lines) > 1:
            text_content = "\n".join(text_lines[1:])  # Exclude the first line

    # Remove lines that contain numbers, punctuation, or start with 'Non.'
    text_lines = text_content.splitlines()
    filtered_lines = [
        line for line in text_lines 
        if not contains_numbers(line) and 
           not is_only_punctuation_or_numbers(line) and 
           not is_line_starting_with_non(line)
    ]
    text_content = "\n".join(filtered_lines).strip()

    # Write to the file
    with open(filename, "w+", encoding="UTF-8") as f:
        f.write(text_content)
    print(f"Saved content for {title} to {filename}")

async def fetch_text_links(url: str) -> List[str]:
    """Fetches all text links from a given author's page."""
    res = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:  # Status ok
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a')  # Get all <a> tags

        for link in links:
            href = link.get('href')
            if href and href.startswith("/loc"):  # Match text links
                full_url = f"https://latin.packhum.org{href}"
                res.append(full_url)
    else:
        print(f"Error: Received status code {response.status_code} for {url}")
    return res

async def crawl_authors(base_url: str = "https://latin.packhum.org/browse") -> List[str]:
    """Crawls the given base page and returns a list of author URLs."""
    res = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:  # Status ok
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a')  # Get all <a> tags

        for link in links:
            href = link.get('href')
            if href and href.startswith("/author/"):  # Match author links
                full_url = f"https://latin.packhum.org{href}"
                res.append(full_url)
    else:
        print(f"Error: Received status code {response.status_code} for {base_url}")
    return res

async def main():
    # Step 1: Get all author links from the base page
    author_links = await crawl_authors()
    print(f"Found {len(author_links)} author links.")

    # Step 2: For each author link, fetch text links and save the texts
    for i, author_link in enumerate(author_links):
        print(f"({i + 1} / {len(author_links)}) Crawling author page: {author_link}")
        
        # Get author name from the link or page
        author_name = author_link.split("/")[-1].replace("author-", "").replace("-", " ").title()

        text_links = await fetch_text_links(author_link)

        for text_link in text_links:
            await fetch_and_save_text(text_link, author_name)

if __name__ == "__main__":
    asyncio.run(main())
