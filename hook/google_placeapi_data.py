import requests
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class GooglePlaceData:
    def __init__(self,
                place_id: str,
                place_name: Optional[str] = None,
                latitude: Optional[float] = None,
                longitude: Optional[float] = None,
                category_code: Optional[str] = None,
                category_description: Optional[str] = None,
                address: Optional[str] = None,
                reference: Optional[str] = None,
                tags: Optional[List[str]] = [],
                user_rating: Optional[float] = None):
        
        self.place_id = place_id
        self.place_name = place_name
        self.latitude = latitude
        self.longitude = longitude
        self.category_code = category_code
        self.category_description = category_description
        self.address = address
        self.reference = reference
        self.tags = tags
        self.user_rating = user_rating

class GooglePlaceAPI:
    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self, language: str):
        self.api_key = os.getenv('GOOGLE_PLACE_API_KEY_V1')  # Load the API key from environment variables
        if not self.api_key:
            raise ValueError("API key not found. Please set the GOOGLE_PLACE_API_KEY_V1 environment variable.")
        self.session = requests.Session()
        self.language = language

    def fetch_search_location(self, keyword: str) -> List[GooglePlaceData]:
        url = f"{self.BASE_URL}/textsearch/json"
        headers = {
            # "Authorization": f"Bearer {self.api_key}",
            "Accept-Language": self.language
        }
        params = {
            "key": self.api_key,
            "query": keyword,
            # "types": "tourist_attraction",
            "language": self.language,
        }

        try:
            # Make the request with SSL verification enabled
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the JSON response
            places_data = response.json().get("results", [])
            return [GooglePlaceData(
                place_id=place["place_id"],
                place_name=place["name"],
                latitude=place.get("geometry", {}).get("location", {}).get("lat"),
                longitude=place.get("geometry", {}).get("location", {}).get("lng"),
                # category_code=place["category_code"],
                # category_description=place["category_description"],
                address=place.get("formatted_address"),
                # reference=place.get("reference"),
                tags=place.get("types"),
                # user_rating=place.get("user_rating")
            ) for place in places_data]

        except requests.exceptions.SSLError as e:
            print("SSL Error: ", e)
            return []
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: ", e)
            return []
    
if __name__ == "__main__":
    # Example usage:
    thai_tourism_api = GooglePlaceAPI("TH")
    
    # Define the search parameters
    search_params = {
        "keyword": "กาญจนบุรี",  # Example keyword for Kanchanaburi
    }

    # Fetch search locations based on the parameters
    recommended_places = thai_tourism_api.fetch_search_location(**search_params)

    for place in recommended_places:
        print(f"Place Name: {place.place_name}, Province: {place.address}, Latitude: {place.latitude}, Longitude: {place.longitude}")
