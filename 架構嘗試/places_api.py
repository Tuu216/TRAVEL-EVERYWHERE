import requests
from typing import Dict, List, Tuple
from config import CONFIG

class PlacesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_lat_lng(self, location: str) -> Tuple[float, float]:
        # 加入國家確保更準確的地理編碼
        full_address = f"{location}, 台灣"
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        response = requests.get(url, params={
            "key": self.api_key,
            "address": full_address,
            "language": "zh-TW"  # 設定語言為繁體中文
        })
        
        print("API Response:", response.json())
        
        if response.status_code != 200:
            raise Exception(f"Geocoding API error: {response.status_code}")
            
        data = response.json()
        if not data['results']:
            raise Exception(f"No results found for location: {location}")
            
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
        

    def fetch_places(self, lat: float, lng: float, radius: int, place_type: str) -> List[Dict]:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "language": "zh-TW"
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Places API error: {response.status_code}")
            
        data = response.json()
        return self._process_places(data.get('results', []))

    def _process_places(self, results: List[Dict]) -> List[Dict]:
        processed = []
        for place in results:
            processed.append({
                'place_id': place['place_id'],
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'location': place['geometry']['location'],
                'rating': place.get('rating'),
                'user_ratings_total': place.get('user_ratings_total'),
                'price_level': place.get('price_level'),
                'tags': self._assign_tags(place.get('types', []))
            })
        return processed

    def _assign_tags(self, types: List[str]) -> List[Tuple[str, str, str]]:
        type_mapping = {
            "tourist_attraction": ("attraction", "藝術人文", "古蹟"),
            "museum": ("museum", "藝術人文", "展覽"),
            "park": ("park", "運動休閒", "自然景觀"),
            "restaurant": ("restaurant", "吃貨天堂", "餐廳"),
            "shopping_mall": ("shopping", "娛樂遊玩", "購物中心")
        }
        
        return [type_mapping[t] for t in types if t in type_mapping]
