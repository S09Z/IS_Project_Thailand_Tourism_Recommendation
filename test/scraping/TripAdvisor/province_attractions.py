import requests
from bs4 import BeautifulSoup

class TripAdvisorScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch_page_content(self, url):
        """Fetch the HTML content of a page."""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to retrieve content from {url}, Status code: {response.status_code}")

    def parse_page(self, content):
        """Parse the HTML content with BeautifulSoup."""
        return BeautifulSoup(content, "html.parser")

    def get_central_thailand_provinces(self):
        """Returns the list of Central Thailand provinces."""
        return [
            "Bangkok", "Ayutthaya", "Nakhon Pathom", "Nonthaburi", 
            "Pathum Thani", "Samut Prakan", "Samut Sakhon", "Lopburi",
            "Suphan Buri", "Saraburi", "Sing Buri", "Ang Thong", "Chachoengsao"
        ]

    def scrape_province_links(self):
        """Scrape province links from the main TripAdvisor attractions page for Thailand."""
        content = self.fetch_page_content(self.base_url)
        soup = self.parse_page(content)

        # Find province links (in the <a> tags with a specific pattern)
        provinces_section = soup.find_all('a', class_='geo_link')

        # Get the list of Central Thailand provinces
        central_provinces = self.get_central_thailand_provinces()

        # List to hold the province links and titles
        province_links = []

        # Loop through all found provinces and extract title and URL
        for province in provinces_section:
            title = province.get_text()
            if any(central_province in title for central_province in central_provinces):
                link = "https://www.tripadvisor.com" + province['href']  # Create the full URL
                province_links.append({'province': title, 'link': link})

        return province_links

    def display_province_links(self, province_links):
        """Display the province links."""
        for province in province_links:
            print(f"Province: {province['province']} - Link: {province['link']}")
    

# Define a subclass for scraping attractions and reviews if needed
class AttractionScraper(TripAdvisorScraper):
    def __init__(self, base_url):
        super().__init__(base_url)

    def scrape_attractions(self, province_url):
        """Scrape the attractions from a given province URL."""
        content = self.fetch_page_content(province_url)
        soup = self.parse_page(content)

        # Find the attraction links
        attractions = soup.find_all('a', class_='attractions-attraction-overview-main-TopPOIs__name--1t28U')

        attraction_links = []
        for attraction in attractions:
            title = attraction.get_text()
            link = "https://www.tripadvisor.com" + attraction['href']
            attraction_links.append({'title': title, 'link': link})

        return attraction_links

    def display_attractions(self, attractions):
        """Display the attractions."""
        for attraction in attractions:
            print(f"Attraction: {attraction['title']} - Link: {attraction['link']}")


# Example usage of the OOP scraper classes
if __name__ == "__main__":
    base_url = "https://www.tripadvisor.com/Attractions-g293915-Activities-Thailand.html"
    
    # Initialize the scraper for provinces
    province_scraper = TripAdvisorScraper(base_url)
    
    # Scrape and display province links
    province_links = province_scraper.scrape_province_links()
    # province_scraper.display_province_links(province_links)
    
    print(province_links)
    
    # Initialize the scraper for attractions in a province (example for Bangkok)
    # attraction_scraper = AttractionScraper(base_url)
    # bangkok_url = "https://www.tripadvisor.com/Attractions-g293916-Activities-Bangkok.html"
    # attractions = attraction_scraper.scrape_attractions(bangkok_url)
    
    # Display attractions in Bangkok
    # attraction_scraper.display_attractions(attractions)
