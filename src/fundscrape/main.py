from fundscrape.nihr_scraper import NihrScraper
import os
import json


def main():
    print("Hello from fundscrape!")
    print(os.getcwd())
    scraper = NihrScraper(funding_freshness_days=5)
    scraper.load_funding_data()



if __name__ == "__main__":
    main()
