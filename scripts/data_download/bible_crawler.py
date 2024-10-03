import asyncio
import requests

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from typing import List

async def crawl_pages(urls: List[str]) -> str:
    """Crawls the given pages, creates the files based on downloaded data, returns XML-formatted metadata to be copied and pasted into sources.xml

    Args:
        urls (List[str]): The list of URLs to crawl

    Returns:
        str: The XML-formatted metadata of the crawled files
    """
    res = ""
    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            for url in urls: # for each page
                result = await crawler.arun(url=f"http://bibleglot.com{url}", css_selector="div.row") # get rows
                text = result.markdown.replace("\\'", "'") # formatting
                extracted_rows = text.split('\n\n') # split rows by language
                extracted_rows = list(filter(lambda x: len(x) > 0, extracted_rows)) # remove empty rows
                sentences_fr = []
                sentences_la = []
                for i, sentence in enumerate(extracted_rows):
                    sentence = sentence.replace("\n", " ")
                    # if i % 3 == 0: Number of the verset (not interesting)
                    if i % 3 == 1: # Latin sentences
                        sentences_la.append(sentence)
                    if i % 3 == 2: # French sentences
                        sentences_fr.append(sentence)
                filename_fr = f"data/raw/data_latin/{url.strip('/').replace('/', '_')}_fr.txt"
                filename_la = f"data/raw/data_latin/{url.strip('/').replace('/', '_')}_la.txt"
                with open(filename_fr, "w+", encoding="UTF-8") as f:
                    output_text = ""
                    for i, sentence in enumerate(sentences_fr):
                        output_text += sentence # add each sentence to the output
                        if i < len(sentences_fr) - 1: # add newline except for the last row
                            output_text += '\n'
                    f.write(output_text)
                    res += f'<item link="{url.strip('/')}" language="french" bilingual="true" filename="{filename_fr}" date="" place="" />\n'
                with open(filename_la, "w+", encoding="UTF-8") as f:
                    output_text = ""
                    for i, sentence in enumerate(sentences_la):
                        output_text += sentence
                        if i < len(sentences_la) - 1:
                            output_text += '\n'
                    f.write(output_text)
                    res += f'<item link="{url.strip('/')}" language="latin" bilingual="true" filename="{filename_la}" date="" place="" />\n'
    except Exception:
        pass
    return res

def get_pages_list(url="http://bibleglot.com/pair/Vulgate/FreSegond") -> List[str]:
    """Retrieves the list of subpage links of a given page

    Args:
        url (str, optional): The URL of the page. Defaults to "http://bibleglot.com/pair/Vulgate/FreSegond".

    Returns:
        List[str]: The list of the URLs of the subpages
    """
    res = []
    response = requests.get(url)

    if response.status_code == 200: # status ok
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a') # get all <a> tags

        for link in links:
            href = link.get('href') # get links
            if href and href not in ['#', '/'] and href.startswith("/pair/Vulgate/FreSegond/"): # check if link is relevant
                res.append(href)
    return res

async def main():
    pages = get_pages_list()
    xml = await crawl_pages(pages)
    with open("tmp.xml", "w+") as f:
        f.write(xml)

if __name__ == "__main__":
    asyncio.run(main())