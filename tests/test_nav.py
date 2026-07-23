import httpx

LISTING_URL = "https://www.nihr.ac.uk/funding-opportunities"
DETAIL_URL = "https://www.nihr.ac.uk/funding/hsdr-researcher-led/2026456"

def test_nav():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/150.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-GB,en;q=0.9",
    }

    with httpx.Client(
        headers=headers,
        follow_redirects=True,
        timeout=30,
    ) as client:

        listing = client.get(DETAIL_URL)
        listing.raise_for_status()

        print("Listing:", listing.status_code)
        print("Cookies:", client.cookies)

        detail = client.get(
            DETAIL_URL,
            headers={"Referer": str(listing.url)},
        )

        print("Detail:", detail.status_code)
        print("WAF:", detail.headers.get("x-amzn-waf-action"))
        print("Server:", detail.headers.get("server"))
        print(detail.text[:5000])

        detail.raise_for_status()