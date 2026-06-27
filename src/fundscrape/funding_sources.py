from fundscrape.funding_source import FundingSource

FUNDING_SOURCES = [
    FundingSource(
       sid="nihr",
       url="https://www.nihr.ac.uk/funding-opportunities",
       scraper_strategy="default" 
    )
]
