from pathlib import Path
from fundscrape.ai_assessor import AIAssessor
from fundscrape.nihr_funding_card import NihrFundingCard
from fundscrape.nihr_detail_page import NihrDetailPage

def test_ai_assessor():
    # we need a test page and a card
    test_page_path = Path(f"tests/test_data/detail_page0.html")
    content = test_page_path.read_bytes()
    detail_page = NihrDetailPage(content,funding_card=NihrFundingCard.dummy_card())

    # setup the ai assessor with this list
    ai_assessor = AIAssessor(
        funding_details=[detail_page],
        ai_params_path="config/ai_params.json",
        ai_prompts_path ="config/ai_prompts.json",
    )

    ai_summary = ai_assessor.make_ai_summary_of_funding_detail_page(detail_page)

if __name__ == "__main__":
    test_ai_assessor()