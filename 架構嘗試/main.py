from database import initialize_database, save_places, query_places
from places_api import get_lat_lng_from_city, fetch_google_places

def main():
    # 初始化資料庫
    initialize_database()

    # 使用者輸入旅遊資訊
    city_name = input("您想去哪個城市旅遊？(必填，例如：台北、新北)：").strip()
    district_name = input("您想去哪個區域？(選填，例如：信義、松山)：").strip()
    full_location = f"{city_name} {district_name}".strip()

    # 搜尋條件
    radius = int(input("請輸入搜尋範圍（單位：公尺，例如：1000）："))
    place_type = input("請輸入想搜尋的地點類型（例如：tourist_attraction, restaurant）：").strip()

    try:
        # 取得經緯度
        location = get_lat_lng_from_city(full_location)

        # 抓取景點資料
        places = fetch_google_places(location, radius, place_type)
        save_places(places)

        # 篩選與顯示結果
        min_rating = float(input("請輸入篩選的最低評分（例如：4.0）："))
        filtered_places = query_places(min_rating)
        print(f"\n符合條件的地點 (評分 >= {min_rating})：")
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
