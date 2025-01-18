import time
import requests
from playwright.async_api import async_playwright

async def fetch_with_captcha_handling(url: str) -> str:
    """Fetch a page and handle CAPTCHA challenges."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=False for debugging
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        # Check if CAPTCHA is displayed
        frame_locator = page.frame_locator("iframe[src*='captcha-delivery']")
        frame = await frame_locator.frame()  # Get the frame object
        if frame:
            print("CAPTCHA detected. Solving...")

            # Extract site_key and page_url
            frame_url = await frame.evaluate("document.location.href")
            site_key = extract_site_key(frame_url)
            captcha_solution = solve_captcha(site_key, url)

            # Submit CAPTCHA solution
            await frame.fill("textarea[name='g-recaptcha-response']", captcha_solution)
            await frame.click("button[type='submit']")  # Adjust selector for CAPTCHA submission

            # Wait for page to reload and continue
            await page.wait_for_load_state("load", timeout=60000)

        # Wait for page content to load
        content = await page.content()
        await browser.close()
        return content

def solve_captcha(site_key: str, page_url: str) -> str:
    """Use a CAPTCHA-solving service to solve the CAPTCHA."""
    api_key = "your_2captcha_api_key"
    
    # Submit CAPTCHA challenge
    response = requests.post(
        "http://2captcha.com/in.php",
        data={
            "key": api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
        },
    )
    captcha_id = response.text.split("|")[1]

    # Wait for solution
    for _ in range(30):
        time.sleep(5)
        solution_response = requests.get(
            f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
        )
        if solution_response.text == "CAPCHA_NOT_READY":
            continue
        return solution_response.text.split("|")[1]

    raise Exception("CAPTCHA solving failed")


def extract_site_key(frame_url: str) -> str:
    """Extract site_key from the CAPTCHA frame URL."""
    from urllib.parse import parse_qs, urlparse
    query_params = parse_qs(urlparse(frame_url).query)
    return query_params.get("k", [None])[0]


# Example usage in the scraping workflow
async def scrape_with_captcha(url: str):
    page_content = await fetch_with_captcha_handling(url)
    # Continue with normal parsing logic
    print("Page content retrieved.")
    return page_content


if __name__ == "__main__":
    import asyncio
    url = "https://www.tripadvisor.com/Attraction_Review-g2154418-d8595756-Reviews-PC_Cowboy_Town-Nong_Bua_Lamphu_Nong_Bua_Lamphu_Province.html"
    asyncio.run(scrape_with_captcha(url))
