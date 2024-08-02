import requests
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Province:
    def __init__(self, name: str):
        self.name = name

class TourismRecommendationSystem:
    BASE_URL = "https://api.tourismauthorityofthailand.com"  # Replace with the actual base URL

    def __init__(self):
        self.api_key = os.getenv('TAT_API_KEY')  # Load the API key from environment variables
        if not self.api_key:
            raise ValueError("API key not found. Please set the TAT_API_KEY environment variable.")
        self.session = requests.Session()

    def fetch_recommend_list(self) -> List[Province]:
        url = f"{self.BASE_URL}/routes"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept-Language": "TH"
        }
        params = {
            "numberofday": 2,
            "geolocation": "13.67,100.76",
            "region": "C"
        }

        response = self.session.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        provinces_data = response.json().get("data", [])
        return [Province(name=province['name']) for province in provinces_data]

# Example usage:
recommendation_system = TourismRecommendationSystem()
recommended_provinces = recommendation_system.fetch_recommend_list()

for province in recommended_provinces:
    print(province.name)
