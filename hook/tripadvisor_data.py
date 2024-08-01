import requests
from requests import Response


class TripadvisorApi():
    def __init__(self, key: str):
        '''
        Tripadvisor Content API wrapper.
        Find official documentation here: https://tripadvisor-content-api.readme.io/

        Args:
            key (str): Your API key.
        '''
        self.api_key = key


    def make_request(self, url: str) -> Response:
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        return response


    def location_details(self, locationId: str, language: str="en", currency: str="USD") -> Response:
        '''
        A Location Details request returns comprehensive information about a location (hotel, restaurant, or an attraction) such as name, address, rating, and URLs for the listing
        on Tripadvisor.

        Args:
            locationId (str): A unique identifier for a location on Tripadvisor. The location ID can be obtained using the Location Search.
            language (str): The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.
            currency (str): The currency code to use for request and response (should follow ISO 4217).

        Returns:
            response (Response): Response object with response data as application/json
        '''
        location_details_url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/details?language={language}&currency={currency}&key={self.api_key}"
        response = self.make_request(location_details_url)
        return response


    def location_photos(self, locationId: str, language: str="en") -> Response:
        '''
        The Location Photos request returns up to 5 high-quality photos for a specific location. Please note that the limits are different for the beta subscribers.
        You need to upgrade to get the higher limits mentioned here. The photos are ordered by recency.

        Args:
            locationId (str): A unique identifier for a location on Tripadvisor. The location ID can be obtained using the Location Search.
            language (str): The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.

        Returns:
            response: Response object with response data as application/json
        '''
        location_photos_url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/photos?language={language}&key={self.api_key}"
        response = self.make_request(location_photos_url)
        return response


    def location_reviews(self, locationId: str, language: str="en") -> Response:
        '''
        The Location Reviews request returns up to 5 of the most recent reviews for a specific location. Please note that the limits are different for the beta subscribers.

        Args:
            locationId (str): A unique identifier for a location on Tripadvisor. The location ID can be obtained using the Location Search.
            language (str): The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.

        Returns:
            response: Response object with response data as application/json
        '''
        location_reviews_url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/reviews?language={language}&key={self.api_key}"
        response = self.make_request(location_reviews_url)
        return response


    def location_search(self, searchQuery: str, category: str = None, phone: str = None, address: str = None, latLong: str = None, radius: int = None, radiusUnit: str = None, language: str = "en") -> Response:
        '''
        The Location Search request returns up to 10 locations found by the given search query. You can use category ("hotels", "attractions", "restaurants", "geos"),
        phone number, address, and latitude/longtitude to search with more accuracy.

        Args:
            searchQuery (str): Text to use for searching based on the name of the location.
            category (str): Filters result set based on property type. Valid options are "hotels", "attractions", "restaurants", and "geos".
            phone (str): Phone number to filter the search results by (this can be in any format with spaces and dashes but without the "+" sign at the beginning).
            address (str): Address to filter the search results by.
            latLong (str): Latitude/Longitude pair to scope down the search around a specifc point - eg. "42.3455,-71.10767".
            radius (int): Length of the radius from the provided latitude/longitude pair to filter results.
            radiusUnit (str): Unit for length of the radius. Valid options are "km", "mi", "m" (km=kilometers, mi=miles, m=meters.
            language (str): The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.

        Returns:
            response: Response object with response data as application/json
        '''
        
        location_search_url = f"https://api.content.tripadvisor.com/api/v1/location/search?language={language}&key={self.api_key}&searchQuery={searchQuery}"

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
        
        response = self.make_request(location_search_url)
        return response


    def location_nearby_search(self, latLong: str, category: str = None, phone: str = None, address: str = None, radius: int = None, radiusUnit: str = None, language: str = "en") -> Response:
        '''
        The Nearby Location Search request returns up to 10 locations found near the given latitude/longtitude.
        You can use category ("hotels", "attractions", "restaurants", "geos"), phone number, address to search with more accuracy.

        Args:
            latLong (str): Latitude/Longitude pair to scope down the search around a specifc point - eg. "42.3455,-71.10767".
            category (str): Filters result set based on property type. Valid options are "hotels", "attractions", "restaurants", and "geos".
            phone (str): Phone number to filter the search results by (this can be in any format with spaces and dashes but without the "+" sign at the beginning).
            address (str): Address to filter the search results by.
            radius (int): Length of the radius from the provided latitude/longitude pair to filter results.
            radiusUnit (str): Unit for length of the radius. Valid options are "km", "mi", "m" (km=kilometers, mi=miles, m=meters.
            language (str): The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.

        Returns:
            response: Response object with response data as application/json
        '''

        location_nearby_url = f"https://api.content.tripadvisor.com/api/v1/location/search?language={language}&key={self.api_key}&latLong={latLong}"

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