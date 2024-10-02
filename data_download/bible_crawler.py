import asyncio
import requests

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from typing import List

async def crawl_pages(urls: List[str]):
    res: List[str] = []
    async with AsyncWebCrawler(verbose=True) as crawler:
        # for url in urls:
        url = urls[0]
        result = await crawler.arun(url=f"http://bibleglot.com{url}", css_selector="div.row")
        res.append(result.markdown)
    for i, row in enumerate(res):
        print(row.split('\n'))
        # TODO Add to file and update sources.xml

def get_pages_list(url="http://bibleglot.com/pair/Vulgate/FreSegond") -> List[str]:
    res = []
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href and href not in ['#', '/'] and href.startswith("/pair/Vulgate/FreSegond/"):
                res.append(href)
    return res

async def main():
    pages = get_pages_list()
    await crawl_pages(pages)

if __name__ == "__main__":
    asyncio.run(main())