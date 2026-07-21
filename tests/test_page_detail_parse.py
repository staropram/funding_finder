from fundscrape.nihr_detail_page import NihrDetailPage
from pathlib import Path
import os


def test_parse_nihr_page():
    # load the html
    test_page_fn = Path("tests/test_data/detail_page1.html")
    content = test_page_fn.read_bytes()
    # setup the page
    detail_page = NihrDetailPage(content)
    print(detail_page)

    # assert stuff, I think we just check for non-empty here
    assert detail_page.overview_main != None
    assert detail_page.overview_timeline != None
    assert detail_page.research_spec != None


if __name__ == "__main__":
    test_parse_nihr_page()