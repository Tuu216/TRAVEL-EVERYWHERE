import requests
from config import API_KEY, TYPE_TO_CATEGORY

print("Used API Key:", API_KEY)

def get_lat_lng_from_city(city_name):
    # 修正地址格式並加入完整參數
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "key": API_KEY,
        "address": city_name,
        "language": "zh-TW",
        "region": "tw",
        "components": "country:TW"
    }

    print("Request URL:", base_url)
    print("Request Params:", params)
    
    response = requests.get(base_url, params=params)
    print("API Response:", response.json())  # 檢查 API 回應
    
    if response.status_code != 200:
        raise Exception(f"Geocoding API 錯誤：{response.status_code}")

    data = response.json()
    if data['status'] == 'REQUEST_DENIED':
        raise Exception("API 金鑰無效或未啟用服務")
    
    results = data.get("results", [])
    if not results:
        raise Exception("無法找到指定地點")

    location = results[0]["geometry"]["location"]
    return f"{location['lat']},{location['lng']}"

def fetch_google_places(location, radius, place_type):
    """使用 Google Places API 抓取附近景點資料。"""
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": location,
        "radius": radius,
        "type": place_type,
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Places API 錯誤：{response.status_code}")

    results = response.json().get("results", [])
    places = []
    for result in results:
        types = result.get("types", [])
        tags = assign_tags(types)
        places.append({
            "name": result.get("name"),
            "address": result.get("vicinity"),
            "rating": result.get("rating"),
            "user_ratings_total": result.get("user_ratings_total"),
            "tags": tags
        })

    return places

def assign_tags(types):
    """根據 Google Places API 的類型分配標籤。"""
    tags = [TYPE_TO_CATEGORY[t] for t in types if t in TYPE_TO_CATEGORY]
    return tags
