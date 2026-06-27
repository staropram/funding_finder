import httpx
from pathlib import Path
from bs4 import BeautifulSoup
import asyncio

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
        # construct the URLs
        # do this asynchronously 5 at a time
        results = await self.fetch_pages(num_pages)

        return funding_data

    async def fetch_pages(self,num_pages):
        sem = asyncio.Semaphore(5)
        tasks = [self.fetch_page(sem,i) for i in range(num_pages)]
        results = await asyncio.gather(*tasks)
        return results

    async def fetch_page(self,sem,page_index):
        async with sem:
            # page fetching code goes here
            print("hi")
            return page_index

    def extract_funding_cards(self):
        self.funding_data

    def setup_http_client(self):
        return httpx.AsyncClient(
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
                "Accept" : "text/html"
            },
            params = {
                "status[Closing soon]": "Closing soon",
                "status[Open]": "Open",
                "status[Opening soon]": "Opening soon",
            }
        )


    def __init__(self,force_reload=False):
        print(f"Loading NIHR page")
        self.url = "https://www.nihr.ac.uk/funding-opportunities?"
        self.cache_file = Path("data/cache/nihr_opportunities.html")
        self.http_client = self.setup_http_client()

        #self.extract_funding_cards()


        

        
