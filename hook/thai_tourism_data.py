import os
import json
from typing import Dict, List, Optional

class Geography:
    """Class representing a geographical region."""

    def __init__(self, geo_id: int, name_th: str, name_en: str):
        self.id = geo_id
        self.name_th = name_th
        self.name_en = name_en

    def __str__(self):
        return f"{self.name_en} ({self.name_th})"

class Amphure:
    """Class representing an amphure (district) within a province."""

    def __init__(self, amphure_data: Dict[str, str]):
        self.name_th = amphure_data.get("name_th", "Unknown Amphure")
        self.name_en = amphure_data.get("name_en", "Unknown Amphure")

    def __str__(self):
        return f"{self.name_en} ({self.name_th})"

class Province:
    """Class representing a province, including its amphures and geography."""

    def __init__(self, province_data: Dict[str, any], geography: Geography):
        self.name_th = province_data.get("name_th", "Unknown Province")
        self.name_en = province_data.get("name_en", "Unknown Province")
        self.geography = geography
        self.amphures = [Amphure(amphure) for amphure in province_data.get("amphure", [])]

    def __str__(self):
        return f"{self.name_en} ({self.name_th})"

    def display_info(self):
        """Prints information about the province and its amphures."""
        for amphure in self.amphures:
            print(f"{self.geography} -> {self} --> {amphure}")

class GeographyLoader:
    """Class responsible for loading and managing geographical data."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.geographies = self._load_geographies()

    def _load_geographies(self) -> Dict[int, Geography]:
        """Load geographies from a JSON file and return a dictionary mapping id to Geography objects."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            geographies_data = json.load(file)
        
        return {
            geo.get("id"): Geography(
                geo["id"],
                geo.get("name_th", "ไม่ทราบภูมิภาค"),
                geo.get("name_en", "Unknown Geography")
            )
            for geo in geographies_data
        }

    def get_geography(self, geo_id: int) -> Optional[Geography]:
        """Retrieve a Geography object by its id."""
        return self.geographies.get(geo_id)

class ProvinceLoader:
    """Class responsible for loading and managing provincial data."""

    def __init__(self, province_file_path: str, geography_loader: GeographyLoader):
        self.province_file_path = province_file_path
        self.geography_loader = geography_loader

    def load_provinces(self) -> List[Province]:
        """Load provinces from a JSON file."""
        with open(self.province_file_path, 'r', encoding='utf-8') as file:
            provinces_data = json.load(file)
        
        provinces = []
        for province_data in provinces_data:
            geography_id = province_data.get("geography_id")
            geography = self.geography_loader.get_geography(geography_id)
            province = Province(province_data, geography)
            provinces.append(province)

        return provinces

def main():
    base_dir = os.path.dirname(__file__)
    province_file_path = os.path.join(base_dir, 'data', 'api_province_with_amphure_tambon.json')
    geography_file_path = os.path.join(base_dir, 'data', 'api_geographies.json')

    geography_loader = GeographyLoader(geography_file_path)
    province_loader = ProvinceLoader(province_file_path, geography_loader)
    provinces = province_loader.load_provinces()

    for province in provinces:
        province.display_info()

if __name__ == "__main__":
    main()
