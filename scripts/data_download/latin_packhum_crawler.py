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

def clean_special_characters(text: str) -> str:
    """Cleans special characters from the text."""
    replacements = {
        '–': '',   # Remove en dash
        '⏑': '',   # Remove special character
        '⏔': '',   # Remove another special character
        '…': '...',  # Replace ellipsis with three dots
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Optionally, remove other unwanted characters (e.g., any non-ASCII characters)
    text = ''.join(c for c in text if ord(c) < 255)
    
    return text

def remove_chevrons(text: str) -> str:
    """Removes all content between < > including the chevrons."""
    return re.sub(r'<[^>]*>', '', text)

def contains_numbers(text: str) -> bool:
    """Returns True if the text contains any numbers."""
    return any(char.isdigit() for char in text)

def is_only_punctuation_or_numbers(text: str) -> bool:
    """Returns True if the text contains only punctuation and/or numbers."""
    return re.fullmatch(r'^[\d\W_]+$', text) is not None

def is_line_starting_with_non(text: str) -> bool:
    """Returns True if the line starts with 'Non.'."""
    return text.startswith("Non.")

def process_text(text: str) -> str:
    """Processes the text according to the specified rules."""
    # Clean special characters and remove chevrons first
    text = clean_special_characters(text)
    text = remove_chevrons(text)

    # Replace ". . ." with "..."
    text = text.replace(". . .", "...")

    # Replace sequences of more than three dots with three dots
    text = re.sub(r'\.{4,}', '...', text)

    # Remove accents
    text = remove_diacritics(text)

    # Convert to lowercase
    text = text.lower()

    # Remove lines that contain only punctuation or start with 'Non.'
    lines = text.splitlines()
    filtered_lines = [
        line for line in lines 
        if line.strip() and not re.fullmatch(r'^[\W_]+$', line.strip())
    ]

    # Join lines with a space instead of a newline
    processed_text = " ".join(filtered_lines).strip()

    # Ensure there's a newline after each punctuation mark
    processed_text = re.sub(r'(?<=[.!?])\s*', '\n', processed_text)  # Newline after punctuation

    # Handle cases where there might be unwanted line breaks
    processed_text = re.sub(r'(\n\s*){2,}', '\n', processed_text)  # Remove extra newlines

    # Prevent unwanted line breaks for lines ending with "..."
    processed_text = re.sub(r'(?<!\.\.\.)\n(?=\s*\.{3})', ' ', processed_text)

    # Remove unwanted line breaks after ellipses
    processed_text = re.sub(r'(?<!\.\.\.)\n(?=\s*\.{4,})', ' ', processed_text)

    # Remove lines that contain only points or are empty
    processed_text = "\n".join(line for line in processed_text.splitlines() if line.strip() and not re.fullmatch(r'^\.+$', line.strip()))

    return processed_text

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
            return save_text_to_file(current_title, content, author_name)

    else:
        print(f"Error: Received status code {response.status_code} for {url}")

def save_text_to_file(title: str, content: List[str], author_name: str):
    """Saves the content to a file with the title as the filename."""
    directory = "texts"  
    os.makedirs(directory, exist_ok=True)
    
    # Clean the title and filename
    clean_title = remove_diacritics(title).replace(" ", "")
    clean_author = remove_diacritics(author_name).replace(" ", "")
    
    # Remove invalid characters for filenames
    invalid_chars = r'<>:"/\\|?*'
    clean_title = re.sub(f'[{re.escape(invalid_chars)}]', '', clean_title)
    clean_author = re.sub(f'[{re.escape(invalid_chars)}]', '', clean_author)
    
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
           not is_line_starting_with_non(line) and
           line.strip()
    ]
    text_content = "\n".join(filtered_lines).strip()

    # Process the text according to the new rules
    text_content = process_text(text_content)

    # Write to the file with UTF-8 encoding
    with open(filename, "w+", encoding="utf-8") as f:
        f.write(text_content)

    # Remove the file if it's empty
    if os.path.getsize(filename) == 0:
        os.remove(filename)
        print(f"Deleted empty file: {filename}")
    else:
        print(f"Saved content for {title} to {filename}")
    return filename

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
    author_urls = await crawl_authors()
    for author_url in author_urls:
        author_name = author_url.split("/")[-1].replace("-", "_")  # Extract author name from URL
        text_urls = await fetch_text_links(author_url)
        for text_url in text_urls:
            await fetch_and_save_text(text_url, author_name)

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
