import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="http://bibleglot.com/pair/Vulgate/FreSegond/Gen.1/")
        print(result.markdown)
        # TODO Improve coding style, extract text from this page and iterate over all the pages, then output this into data_latin and update sources.xml

if __name__ == "__main__":
    asyncio.run(main())