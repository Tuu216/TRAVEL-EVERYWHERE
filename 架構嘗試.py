import requests
import sqlite3

def fetch_google_places(api_key, location, radius, place_type):
    """
    Fetch recommended places from Google Places API.

    Parameters:
    - api_key (str): Google API Key.
    - location (str): Latitude and longitude in "lat,lng" format.
    - radius (int): Search radius in meters.
    - place_type (str): Type of place to search (e.g., 'park', 'museum').

    Returns:
    - list of dict: List of recommended places with details.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": location,
        "radius": radius,
        "type": place_type,
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error with Google Places API: {response.status_code}")

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

def get_lat_lng_from_city(api_key, city_name):
    """
    Convert city name to latitude and longitude using Google Geocoding API.

    Parameters:
    - api_key (str): Google API Key.
    - city_name (str): Name of the city to convert.

    Returns:
    - str: Latitude and longitude in "lat,lng" format.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "key": api_key,
        "address": city_name,
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error with Google Geocoding API: {response.status_code}")

    results = response.json().get("results", [])

    if not results:
        raise Exception("No results found for the specified city.")

    location = results[0]["geometry"]["location"]
    return f"{location['lat']},{location['lng']}"

def assign_tags(types):
    """
    Assign tags based on Google Places API types.

    Parameters:
    - types (list of str): List of types from Google Places API.

    Returns:
    - list of tuple: Assigned tags as (Level 1, Level 2).
    """
    type_to_category = {
        "tourist_attraction": ("藝術人文", "古蹟"),
        "museum": ("藝術人文", "展覽"),
        "park": ("運動休閒", "自然景觀"),
        "natural_feature": ("運動休閒", "自然景觀"),
        "amusement_park": ("娛樂遊玩", "主題樂園"),
        "zoo": ("娛樂遊玩", "動物園"),
        "aquarium": ("娛樂遊玩", "水族館"),
        "restaurant": ("吃貨天堂", "餐廳"),
        "cafe": ("吃貨天堂", "飲料冰品"),
        "bar": ("吃貨天堂", "飲料冰品"),
        "casino": ("娛樂遊玩", "賭場"),
        "shopping_mall": ("娛樂遊玩", "購物中心"),
        "night_club": ("娛樂遊玩", "夜生活"),
        "church": ("藝術人文", "宗教"),
        "hindu_temple": ("藝術人文", "宗教"),
        "mosque": ("藝術人文", "宗教"),
        "synagogue": ("藝術人文", "宗教"),
        "spa": ("運動休閒", "休閒養生"),
        "gym": ("運動休閒", "健身"),
        "stadium": ("運動休閒", "體育場"),
        "food": ("吃貨天堂", "小吃"),
        "lodging": ("運動休閒", "休閒養生"),
        "art_gallery": ("藝術人文", "展覽"),
        "landmark": ("藝術人文", "古蹟")
    }

    tags = []
    for t in types:
        if t in type_to_category:
            tags.append(type_to_category[t])
    return tags

def save_to_database(places):
    """
    Save fetched places to SQLite database.

    Parameters:
    - places (list of dict): List of places with details to save.
    """
    conn = sqlite3.connect("places.db")
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM places")

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            tags TEXT
        )
    ''')

    # Insert data into the table
    for place in places:
        cursor.execute('''
            INSERT INTO places (name, address, rating, user_ratings_total, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (place["name"], place["address"], place["rating"], place["user_ratings_total"], str(place["tags"])))

    conn.commit()
    conn.close()

def filter_places(min_rating=0, max_results=10):
    """
    Query and filter places from the database based on minimum rating.

    Parameters:
    - min_rating (float): Minimum rating to filter places.
    - max_results (int): Maximum number of results to return.

    Returns:
    - list of dict: Filtered places.
    """
    conn = sqlite3.connect("places.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, address, rating, user_ratings_total, tags
        FROM places
        WHERE rating >= ?
        ORDER BY rating DESC
        LIMIT ?
    ''', (min_rating, max_results))

    results = cursor.fetchall()
    conn.close()

    filtered_places = [
        {
            "name": row[0],
            "address": row[1],
            "rating": row[2],
            "user_ratings_total": row[3],
            "tags": row[4]
        } for row in results
    ]

    return filtered_places

def main():
    # 預設使用的 Google API 金鑰
    API_KEY = "AIzaSyBrNGZNFHQfvy9zMTjmDNfNu9Pah1aP5eI"

    # 詢問使用者想旅遊的城市和地區
    city_name = input("您想去哪個城市旅遊？(必填，例如：台北、新北)：").strip()
    district_name = input("您想去哪個區域？(選填，例如：信義、松山)：").strip()

    # 組合城市和區域名稱
    full_location = city_name
    if district_name:
        full_location += f" {district_name}"

    try:
        # 透過 Google Geocoding API 獲取經緯度
        location = get_lat_lng_from_city(API_KEY, full_location)

        # 提示使用者輸入搜尋範圍和類型
        radius = int(input("請輸入搜尋範圍（單位：公尺，例如：1000）："))
        place_type = input("請輸入想搜尋的地點類型（例如：tourist_attraction, restaurant）：")

        # 抓取 Google Places API 資料並存入資料庫
        places = fetch_google_places(API_KEY, location, radius, place_type)
        save_to_database(places)

        # 提示使用者輸入篩選條件
        min_rating = float(input("請輸入篩選的最低評分（例如：4.0）："))
        print(f"\n符合條件的地點 (評分 >= {min_rating})：")

        # 從資料庫篩選並顯示結果
        filtered_places = filter_places(min_rating)
        for idx, place in enumerate(filtered_places, start=1):
            print(f"{idx}. {place['name']}")
            print(f"   地址：{place['address']}")
            print(f"   評分：{place['rating']} ({place['user_ratings_total']} 則評價)")
            print(f"   標籤：{place['tags']}")
            print("----------------------------------")

    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == "__main__":
    main()
