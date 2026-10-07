from fundscrape.nihr_scraper import NihrScraper
from fundscrape.ai_assessor import AIAssessor
from fundscrape.html_generator import HTMLGenerator
from pathlib import Path
import os
import json


def main():
    # setup the scraper, this will fetch the latest opportunities
    scraper = NihrScraper(funding_freshness_days=5,force_reload=False)
    # assess each thing
    ai_assessor = AIAssessor(
        scraper.funding_details,
        ai_params_path="config/ai_params.json",
        ai_prompts_path ="config/ai_prompts.json",
    )

    # load funding objectives
    ai_objectives_path = "config/ai_objectives.json"
    with Path(ai_objectives_path).open(encoding="utf-8") as file:
        objectives = json.load(file)

    ai_responses = ai_assessor.assess_objectives_against_summaries(objectives)

    for name, response in ai_responses.items():
        html_generator = HTMLGenerator(response,name)
        html_generator.to_html()


if __name__ == "__main__":
    main()
