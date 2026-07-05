import re
import httpx
import asyncio
from hashlib import sha256
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dataclasses import dataclass
from fundscrape.nihr_funding_card import NihrFundingCard

class NihrScraper:
    async def load_funding_data(self,force_reload=False):
        # load the cached top level search if it doesn't exist or is requested
        if self.cache_file.exists() and force_reload==False:
            print("Cached top level file exists, loading")
            html_text = self.cache_file.read_text()

            funding_data = BeautifulSoup(
                self.cache_file.read_text(),
                "lxml"
            )
        else:
            print("Top-level does not exist, fetching")
            req = self.http_client.get(self.url)
            if req.status_code != 200:
                print(f"Not OK: code={req.status_code}")
                print(req.content)
                exit()

            # cache the content
            print("Writing requested HTML")
            self.cache_file.write_bytes(req.content)
            funding_data = BeautifulSoup(req.content,"lxml")

        # fetch each page
        num_pages = int(funding_data.find("li",class_="page-item--last").find_all("span")[-1].text)
        print(f"We have {num_pages} pages to fetch")
        # get the funding cards
        funding_cards = await self.fetch_funding_card_pages(num_pages)
        # now fetch the actual details
        funding_details = await self.fetch_funding_detail_pages(funding_cards)

        return funding_details

    async def fetch_funding_detail_page(self,sem,i,funding_card):
        async with sem:
            # we don't want any params
            params = self.http_client.params
            # use hash of URL for cache name
            url = funding_card.link
            digest = sha256(url.encode("utf-8")).hexdigest()
            cached_fn = Path(f"data/cache/{digest}")
            if cached_fn.exists():
                print(f"loading cached data for URL {url}")
                content = cached_fn.read_text()
            else:
                print(f"fetching data for URL {url}")
                # note use empty query params
                req = await self.http_client.get(url=url,params=httpx.QueryParams())
                content = req.content
                cached_fn.write_bytes(content)

            print(content)
            return None

    async def fetch_funding_detail_pages(self,funding_cards):
        sem = asyncio.Semaphore(1)
        tasks = [self.fetch_funding_detail_page(sem,i,funding_cards[i]) for i in range(1,len(funding_cards))]
        results = await asyncio.gather(*tasks)
        return results

    async def fetch_funding_card_pages(self,num_pages):
        sem = asyncio.Semaphore(1)
        tasks = [self.fetch_funding_card_page(sem,i) for i in range(1,num_pages)]
        results = await asyncio.gather(*tasks)
        # flatten this into a single list
        flat_results = [
            funding_card 
            for page_of_cards in results
            for funding_card in page_of_cards
        ]
        return flat_results

    async def fetch_funding_card_page(self,sem,page_index):
        async with sem:
            # adjust params
            params = self.http_client.params
            params = params.set("page",page_index)
            # page fetching code goes here
            print(params)
            cached_fn = Path(f"data/cache/nihr_page{page_index}")
            if cached_fn.exists():
                print(f"loading cached data for page {page_index}")
                content = cached_fn.read_text()
            else:
                print(f"fetching data for page {page_index}")
                req = await self.http_client.get(self.url,params=params)
                cached_fn.write_bytes(req.content)
                content = req.content
            
            page_data = BeautifulSoup(content,"lxml")
        
            # extract the funding cards
            funding_card_divs = page_data.find_all("div",class_="node--type-funding-opportunity")
            funding_cards = []
            for fcd in funding_card_divs:
                try:
                    funding_cards.append(NihrFundingCard(fcd))
                except Exception as e:
                    print("Failed to parse funding card: ",e)
                    print(fcd.getText())
            
            return funding_cards


    def setup_http_client(self):
        return httpx.AsyncClient(
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept" : "text/html"
            },
            params = {
                "status[Closing soon]": "Closing soon",
                "status[Open]": "Open",
                "status[Opening soon]": "Opening soon"
            }
        )


    def __init__(self,force_reload=False):
        print(f"Loading NIHR page")
        self.url = "https://www.nihr.ac.uk/funding-opportunities?"
        self.cache_file = Path("data/cache/nihr_opportunities.html")
        self.http_client = self.setup_http_client()

        #self.extract_funding_cards()


        

        
