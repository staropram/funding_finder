from fundscrape.nihr_scraper import NihrScraper
import os
import asyncio

async def main():
    print("Hello from fundscrape!")
    print(os.getcwd())
    scraper = NihrScraper()
    await scraper.load_funding_data()



if __name__ == "__main__":
    asyncio.run(main())
