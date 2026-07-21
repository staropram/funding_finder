import re
import time
import httpx
import asyncio
import random
from hashlib import sha256
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dataclasses import dataclass
from fundscrape.nihr_funding_card import NihrFundingCard

class NihrScraper:
    def load_funding_data(self,force_reload=False):
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
        funding_cards = self.fetch_funding_card_pages(num_pages)
        # now fetch the actual details
        funding_details = self.fetch_funding_detail_pages(funding_cards)

        return funding_details

    def fetch_url_with_retries(self,url,max_retries=3,params=None):
        for attempt in range(1,max_retries+1):
            try:
                print(f"Attempting to fetch {url}")
                response = self.http_client.get(url=url,params=params)
                response.raise_for_status()
                return response.content
            except (httpx.TimeoutException,httpx.TransportError) as e:
                if attempt==max_retries:
                    raise

                wait = attempt * 3
                print(f"Fetch failed for {url}: {e}. Retrying in {wait}s")
                time.sleep(wait)

            except httpx.HTTPStatusError as e:
                status = e.response.status_code

                if status in (429, 500, 502, 503, 504):
                    if attempt == max_retries:
                        raise

                    wait = attempt * 5
                    print(f"HTTP {status} for {url}. Retrying in {wait}s")
                    time.sleep(wait)
                else:
                    raise
            



    def fetch_url_cached(self,url,cached_fn,max_retries=3,params=None,force_reload=False):
        if cached_fn.exists() and not force_reload:
            print(f"loading cached data for URL {url}")
            return cached_fn.read_bytes()

        content = self.fetch_url_with_retries(url,max_retries=max_retries,params=params)
        print(f"Writing cached file for {url}")
        cached_fn.write_bytes(content)

        # force a little random sleep
        delay = random.uniform(1, 3)
        print(f"Sleeping for {delay:.1f}s")
        time.sleep(delay)

        return content

    def fetch_funding_detail_page(self,funding_card):
        # we don't want any params
        params = self.http_client.params
        # use hash of URL for cache name
        url = funding_card.link.replace(
            "https://nihr.ac.uk/",
            "https://www.nihr.ac.uk/",
        )
        digest = sha256(url.encode("utf-8")).hexdigest()
        cached_fn = Path(f"data/cache/{digest}")
        content = self.fetch_url_cached(url=url,cached_fn=cached_fn)

        return None

    def fetch_funding_detail_pages(self,funding_cards):
        results = []
        for funding_card_index in range(0,len(funding_cards)):
            results.append(self.fetch_funding_detail_page(funding_cards[funding_card_index]))
        return results

    def fetch_funding_card_pages(self,num_pages):
        results = []
        for page_number in range(0,num_pages):
            results.append(self.fetch_funding_card_page(page_number))
        # flatten this into a single list
        flat_results = [
            funding_card 
            for page_of_cards in results
            for funding_card in page_of_cards
        ]
        return flat_results

    def fetch_funding_card_page(self,page_number):
        # adjust params
        params = self.funding_params.set("page",page_number)
            
        cached_fn = Path(f"data/cache/nihr_page{page_number}")
        print(f"fetching data for page {page_number}")
        content = self.fetch_url_cached(
            url=self.main_funding_endpoint,
            cached_fn=cached_fn,
            params=params
        )
        
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
        return httpx.Client(
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-GB,en;q=0.9"
            },
            follow_redirects=True,
            timeout=httpx.Timeout(30.0)
        )


    def __init__(self,force_reload=False):
        print(f"Loading NIHR page")
        self.main_funding_endpoint = "https://www.nihr.ac.uk/funding-opportunities?"
        self.cache_file = Path("data/cache/nihr_opportunities.html")
        self.funding_params = httpx.QueryParams({
            "status[Closing soon]": "Closing soon",
            "status[Open]": "Open",
            "status[Opening soon]": "Opening soon"
        })
        self.http_client = self.setup_http_client()

        #self.extract_funding_cards()


        

        
