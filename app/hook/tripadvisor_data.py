import requests
from requests import Response

class TripAdvisorApi:
    def __init__(self, key: str, language: str):
        self.api_key = key
        self.language = language
        self.api_url = 'https://api.content.tripadvisor.com/api/v1'

    def make_request(self, url: str) -> Response:
        headers = {"accept": "application/json", "Accept-Language": self.language}
        response = requests.get(url, headers=headers)
        return response

    def location_details(self, locationId: str, language: str = "th", currency: str = "USD") -> Response:
        location_details_url = f"{self.api_url}/location/{locationId}/details?language={language}&currency={currency}&key={self.api_key}"
        response = self.make_request(location_details_url)
        return response

    def location_photos(self, locationId: str, language: str = "th") -> Response:
        location_photos_url = f"{self.api_url}/location/{locationId}/photos?language={language}&key={self.api_key}"
        response = self.make_request(location_photos_url)
        return response

    def location_reviews(self, locationId: str, language: str = "th") -> Response:
        location_reviews_url = f"{self.api_url}/location/{locationId}/reviews?language={language}&key={self.api_key}"
        response = self.make_request(location_reviews_url)
        return response

    def location_search(self, searchQuery: str, category: str = None, phone: str = None, address: str = None,
                        latLong: str = None, radius: int = None, radiusUnit: str = None,
                        language: str = "en") -> str:
        location_search_url = f"{self.api_url}/location/search?language={language}&key={self.api_key}&searchQuery={searchQuery}"

        if category:
            location_search_url += f"&category={category}"
        if phone:
            location_search_url += f"&phone={phone}"
        if address:
            location_search_url += f"&address={address}"
        if latLong:
            location_search_url += f"&latLong={latLong}"
        if radius:
            location_search_url += f"&radius={radius}"
        if radiusUnit:
            location_search_url += f"&radiusUnit={radiusUnit}"
        # print(f">>> make request [{location_search_url}]")
        response = self.make_request(location_search_url)
        return response

    def location_nearby_search(self, latLong: str, category: str = None, phone: str = None, address: str = None,
                               radius: int = None, radiusUnit: str = None, language: str = "en") -> Response:
        location_nearby_url = f"{self.api_url}/location/search?language={language}&key={self.api_key}&latLong={latLong}"

        if category:
            location_nearby_url += f"&category={category}"
        if phone:
            location_nearby_url += f"&phone={phone}"
        if address:
            location_nearby_url += f"&address={address}"
        if radius:
            location_nearby_url += f"&radius={radius}"
        if radiusUnit:
            location_nearby_url += f"&radiusUnit={radiusUnit}"

        response = self.make_request(location_nearby_url)
        return response

    def test_api_request(self) -> Response:
        print(f"Testing Tripadvisor API... {self.api_key}")

        search_query = "เมืองกาญจนบุรี"
        url = f"{self.api_url}/location/search"

        headers = {"accept": "application/json"}

        params = {
            "key": self.api_key,
            "searchQuery": search_query,
            "category": "attractions",
            "language": "th"
        }

        response = requests.get(url, headers=headers, params=params)
        print(response.text)
        return response

# if __name__ == "__main__":
#     # Example usage:
#     thai_tourism_api = TripAdvisorApi('')
#     thai_tourism_api.test_api_request()
