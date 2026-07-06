from fundscrape.nihr_scraper import NihrScraper
import os

def main():
    print("Hello from fundscrape!")
    print(os.getcwd())
    scraper = NihrScraper()
    scraper.load_funding_data()



if __name__ == "__main__":
    main()
