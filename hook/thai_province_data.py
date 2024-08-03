import requests
from dataclasses import dataclass
from typing import List

@dataclass
class Province:
    name: str

class ThaiGeographiesAPI:
    BASE_URL = "https://thaiaddressapi-thaikub.herokuapp.com/v1"

    def __init__(self):
        self.session = requests.Session()

    def fetch_all_provinces(self) -> List[Province]:
        url = f"{self.BASE_URL}/thailand/provinces"
        response = self.session.get(url)
        response.raise_for_status()
        provinces_data = response.json().get("data", [])
        return [Province(name=province) for province in provinces_data]

    def fetch_districts_in_province(self, province_name: str) -> List[str]:
        url = f"{self.BASE_URL}/thailand/provinces/{province_name}/district"
        response = self.session.get(url)
        response.raise_for_status()
        districts_data = response.json().get("data", [])
        return districts_data

    def fetch_subdistricts_in_district(self, province_name: str, district_name: str) -> List[str]:
        url = f"{self.BASE_URL}/thailand/provinces/{province_name}/district/{district_name}"
        response = self.session.get(url)
        response.raise_for_status()
        subdistricts_data = response.json().get("data", [])
        return subdistricts_data

# Example usage
if __name__ == "__main__":
    api = ThaiGeographiesAPI()
    
    # Fetch all provinces
    provinces = api.fetch_all_provinces()
    for province in provinces:
        print(province.name)
    
    # Fetch all districts in a specific province
    province_name = "กรุงเทพ"
    districts = api.fetch_districts_in_province(province_name)
    for district in districts:
        print(district)
    
    # Fetch all subdistricts in a specific district of a specific province
    district_name = "บางรัก"
    subdistricts = api.fetch_subdistricts_in_district(province_name, district_name)
    for subdistrict in subdistricts:
        print(subdistrict)
