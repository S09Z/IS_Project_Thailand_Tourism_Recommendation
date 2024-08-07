import requests
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class ThaiTourismData:
    def __init__(self, place_id: str, place_name: str, latitude: float, longitude: float,
                 category_code: str, category_description: str, sha_name: Optional[str],
                 sha_type_code: Optional[str], sha_type_description: Optional[str], sha_cate_id: Optional[str],
                 sha_cate_description: Optional[str], address: Optional[str], sub_district: str,
                 district: str, province: str, postcode: str, thumbnail_url: Optional[str],
                 destination: str, tags: Optional[List[str]], distance: float, update_date: str):
        self.place_id = place_id
        self.place_name = place_name
        self.latitude = latitude
        self.longitude = longitude
        self.category_code = category_code
        self.category_description = category_description
        self.sha_name = sha_name
        self.sha_type_code = sha_type_code
        self.sha_type_description = sha_type_description
        self.sha_cate_id = sha_cate_id
        self.sha_cate_description = sha_cate_description
        self.address = address
        self.sub_district = sub_district
        self.district = district
        self.province = province
        self.postcode = postcode
        self.thumbnail_url = thumbnail_url
        self.destination = destination
        self.tags = tags
        self.distance = distance
        self.update_date = update_date

class ThaiTourismAPI:
    BASE_URL = "https://tatapi.tourismthailand.org/tatapi/v5/places"

    def __init__(self, language: str):
        self.api_key = os.getenv('TAT_API_KEY')  # Load the API key from environment variables
        if not self.api_key:
            raise ValueError("API key not found. Please set the TAT_API_KEY environment variable.")
        self.session = requests.Session()
        self.language = language

    def fetch_search_location(self, keyword: str, location: str, categorycodes: str,
                              province_name: str, radius: int, number_of_result: int,
                              page_number: int, destination: str, filter_by_update_date: str) -> List[ThaiTourismData]:
        url = f"{self.BASE_URL}/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept-Language": self.language
        }
        params = {
            "keyword": keyword,
            "location": location,
            "categorycodes": categorycodes,
            "provinceName": province_name,
            "radius": radius,
            "numberOfResult": number_of_result,
            "pagenumber": page_number,
            # "destination": destination,
            # "filterByUpdateDate": filter_by_update_date
        }

        try:
            # Make the request with SSL verification enabled
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the JSON response
            places_data = response.json().get("result", [])
            return [ThaiTourismData(
                place_id=place["place_id"],
                place_name=place["place_name"],
                latitude=place["latitude"],
                longitude=place["longitude"],
                category_code=place["category_code"],
                category_description=place["category_description"],
                sha_name=place["sha"]["sha_name"],
                sha_type_code=place["sha"]["sha_type_code"],
                sha_type_description=place["sha"]["sha_type_description"],
                sha_cate_id=place["sha"]["sha_cate_id"],
                sha_cate_description=place["sha"]["sha_cate_description"],
                address=place["location"]["address"],
                sub_district=place["location"]["sub_district"],
                district=place["location"]["district"],
                province=place["location"]["province"],
                postcode=place["location"]["postcode"],
                thumbnail_url=place["thumbnail_url"],
                destination=place["destination"],
                tags=place.get("tags"),  # Use .get() to handle potential None values
                distance=place["distance"],
                update_date=place["update_date"]
            ) for place in places_data]

        except requests.exceptions.SSLError as e:
            print("SSL Error: ", e)
            return []
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: ", e)
            return []
    
if __name__ == "__main__":
    # Example usage:
    thai_tourism_api = ThaiTourismAPI()
    
    # Define the search parameters
    search_params = {
        "keyword": "กาญจนบุรี",  # Example keyword for Kanchanaburi
        "location": "13.6904831,100.5226014",
        "categorycodes": "RESTAURANT",
        "province_name": "Bangkok",
        "radius": 20,
        "number_of_result": 10,
        "page_number": 1,
        "destination": "Bangkok",
        "filter_by_update_date": "2019/09/01-2021/12/31"
    }

    # Fetch search locations based on the parameters
    recommended_places = thai_tourism_api.fetch_search_location(**search_params)

    for place in recommended_places:
        print(f"Place Name: {place.place_name}, Province: {place.province}, Latitude: {place.latitude}, Longitude: {place.longitude}")
