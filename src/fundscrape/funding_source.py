from dataclasses import dataclass

@dataclass
class FundingSource:
    sid : str
    url : str
    scraper_strategy : str