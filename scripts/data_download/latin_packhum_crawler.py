import asyncio
import requests
from bs4 import BeautifulSoup
from typing import List

async def crawl_authors(base_url: str = "https://latin.packhum.org/browse") -> List[str]:
    """Crawls the given base page and returns a list of author URLs.

    Args:
        base_url (str): The URL of the base page to crawl.

    Returns:
        List[str]: A list of URLs for the authors found on the page.
    """
    res = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:  # status ok
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a')  # get all <a> tags

        # Debug: Print all href attributes found to check their format
        for link in links:
            href = link.get('href')
            print(f"Found link: {href}")  # Print each href to see what is being captured
            if href and href.startswith("/author/"):  # Adjusted to match the format used on the site
                full_url = f"https://latin.packhum.org{href}"
                res.append(full_url)
    else:
        print(f"Error: Received status code {response.status_code}")
    return res

async def main():
    author_links = await crawl_authors()
    print(author_links)  # This should now show a list of author URLs if the function works correctly

if __name__ == "__main__":
    asyncio.run(main())
