# this encodes the source
from dataclasses import dataclass

@dataclass
class FundingSource:
    source_id: str
    url: str
    scrape_strategy: str