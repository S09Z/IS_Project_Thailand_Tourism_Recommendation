import asyncio
import json
import math
from typing import List, Dict, Optional
from httpx import AsyncClient
from bs4 import BeautifulSoup

client = AsyncClient(
    headers={
        # Use the same headers as a popular web browser (Chrome on Windows in this case)
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
    },
    follow_redirects=True
)

def parse_attraction_page(response: str) -> Dict:
    """Parse attraction data from the page"""
    soup = BeautifulSoup(response, 'html.parser')

    # Extract basic data like aggregate rating and review count
    script_tag = soup.find("script", string=lambda t: "aggregateRating" in t if t else False)
    basic_data = json.loads(script_tag.string) if script_tag else {}
    
    description = soup.select_one("div.fIrGe._T").get_text(strip=True) if soup.select_one("div.fIrGe._T") else None
    amenities = [feature.get_text(strip=True) for feature in soup.select("div[data-test-target='amenity']")]

    # Extract reviews
    reviews = []
    for review in soup.select("div[data-reviewid]"):
        title_element = review.select_one("div[data-test-target='review-title'] a span span")
        text_element = review.select_one("span[data-test-target='review-text'] span")
        rate_element = review.select_one("div[data-test-target='review-rating'] span")
        trip_data_element = review.find("span", string=lambda t: "Date of stay" in t if t else False)

        title = title_element.get_text(strip=True) if title_element else None
        text = text_element.get_text(strip=True) if text_element else None
        rate = int(rate_element['class'][-1].split("_")[-1]) if rate_element else None
        trip_data = trip_data_element.get_text(strip=True) if trip_data_element else None

        reviews.append({
            "title": title,
            "text": text,
            "rate": rate,
            "tripDate": trip_data
        })

    return {
        "basic_data": basic_data,
        "description": description,
        "features": amenities,
        "reviews": reviews
    }


async def scrape_attraction(url: str, max_review_pages: Optional[int] = None) -> Dict:
    """Scrape attraction data and reviews"""
    first_page = await client.get(url)
    assert first_page.status_code != 403, "Request is blocked"
    attraction_data = parse_attraction_page(first_page.text)

    # Get the number of total review pages
    _review_page_size = 10
    total_reviews = int(attraction_data["basic_data"].get("aggregateRating", {}).get("reviewCount", 0))
    total_review_pages = math.ceil(total_reviews / _review_page_size)

    # Get the number of review pages to scrape
    if max_review_pages and max_review_pages < total_review_pages:
        total_review_pages = max_review_pages
    
    # Scrape all review pages concurrently
    review_urls = [
        url.replace("-Reviews-", f"-Reviews-or{_review_page_size * i}-")
        for i in range(1, total_review_pages)
    ]
    
    for response in asyncio.as_completed([client.get(url) for url in review_urls]):
        page = await response
        data = parse_attraction_page(page.text)
        attraction_data["reviews"].extend(data["reviews"])
    
    print(f"Scraped attraction data with {len(attraction_data['reviews'])} reviews")
    return attraction_data


# Example usage:
# asyncio.run(scrape_attraction("https://www.tripadvisor.com/Attraction_Review-g60763-d104365-Reviews-Central_Park-New_York_City_New_York.html"))

async def run():
    hotel_data = await scrape_attraction(
        url="https://www.tripadvisor.com/Attraction_Review-g60763-d104365-Reviews-Central_Park-New_York_City_New_York.html"    ,
        max_review_pages=3,    
    )
    # print the result in JSON format
    print(json.dumps(hotel_data, indent=2))

if __name__ == "__main__":
    asyncio.run(run())