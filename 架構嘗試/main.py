from config import CONFIG
from database import Database
from places_api import PlacesAPI

def display_menu():
    print("\n請選擇要搜尋的地點類型：")
    for key, (_, name) in CONFIG["PLACE_TYPES"].items():
        print(f"{key}. {name}")
    return input("請輸入選項編號（可多選，用逗號分隔）：").split(",")

def main():
    db = Database(CONFIG["DB_NAME"])
    api = PlacesAPI(CONFIG["API_KEY"])

    try:
        # 使用者輸入
        city = input("請輸入想去的城市（例如：台北）：").strip()
        district = input("請輸入行政區（可選，例如：信義）：").strip()
        location = f"{city} {district}".strip()
        
        # 取得經緯度
        lat, lng = api.get_lat_lng(location)
        
        # 選擇地點類型
        type_choices = display_menu()
        
        # 搜尋地點
        all_places = []
        for choice in type_choices:
            if choice in CONFIG["PLACE_TYPES"]:
                place_type, _ = CONFIG["PLACE_TYPES"][choice]
                places = api.fetch_places(lat, lng, CONFIG["DEFAULT_RADIUS"], place_type)
                all_places.extend(places)
        
        # 儲存結果
        db.save_places(all_places)
        
        # 篩選顯示
        min_rating = float(input("\n請輸入最低評分（1-5）："))
        filtered_places = db.get_filtered_places(min_rating, CONFIG["MAX_RESULTS"])
        
        print("\n搜尋結果：")
        for idx, place in enumerate(filtered_places, 1):
            print(f"\n{idx}. {place['name']}")
            print(f"   地址：{place['address']}")
            print(f"   評分：{place['rating']} ({place['user_ratings_total']} 則評價)")
            print(f"   分類：{', '.join(f'{tag[1]}-{tag[2]}' for tag in place['tags'])}")

    except Exception as e:
        print(f"錯誤：{e}")

if __name__ == "__main__":
    main()