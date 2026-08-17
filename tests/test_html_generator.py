import json
from fundscrape.html_generator import HTMLGenerator
from pathlib import Path

def test_ai_assessor():
    # load the dummy data
    ai_response_filename = Path("tests/test_data/kidney_ai_response.txt")
    with ai_response_filename.open() as file:
        ai_response = file.read()

    # setup the HTMLGenerator
    html_generator = HTMLGenerator(ai_response)

    html_generator.to_html("tests/test_data/kidney_ai_response.html")


if __name__ == "__main__":
    test_ai_assessor()