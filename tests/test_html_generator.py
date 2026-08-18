import json
from fundscrape.html_generator import HTMLGenerator
from pathlib import Path

def test_ai_assessor():
    # load the dummy data
    ranked_assessments_filename = Path("tests/test_data/kidney_data_final_ranking.json")
    with ranked_assessments_filename.open() as file:
        ranked_assessments = json.load(file)

    # setup the HTMLGenerator
    html_generator = HTMLGenerator(ranked_assessments)

    html_generator.to_html("tests/test_data/kidney_ranked_assessments.html")


if __name__ == "__main__":
    test_ai_assessor()