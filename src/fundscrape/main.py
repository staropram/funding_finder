from fundscrape.nihr_scraper import NihrScraper
from fundscrape.ai_assessor import AIAssessor
import os
import json


def main():
    # setup the scraper, this will fetch the latest opportunities
    scraper = NihrScraper(funding_freshness_days=5,force_reload=False)
    ai_assessor = AIAssessor(scraper.funding_details)




if __name__ == "__main__":
    main()
