import requests
import sqlite3
import time

# API 設定
API_KEY = 'AIzaSyAU35K8XohOeEW7u8tiXfi3hwi5hzFCaCY'
BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
QUERY = '台北美食'

# 建立 SQLite 資料庫並創建表格
def init_db():
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            place_id TEXT UNIQUE,
            query TEXT  -- 新增 query 欄位來儲存查詢關鍵字
        )
    ''')
    conn.commit()
    conn.close()

# 獲取景點資料
def fetch_places(query):
    params = {
        'query': query,
        'key': API_KEY
    }
    all_results = []
    
    while True:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code != 200 or 'results' not in data:
            print("API 請求失敗:", data.get('error_message', 'Unknown error'))
            break
        
        all_results.extend(data['results'])
        
        # 檢查是否有下一頁
        next_page_token = data.get('next_page_token')
        if next_page_token:
            print("獲取下一頁資料...")
            params['pagetoken'] = next_page_token
            time.sleep(2)  # 等待2秒，確保 token 生效
        else:
            break
    
    return all_results

# 儲存景點資料到資料庫
def save_to_db(places, query):
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    for place in places:
        try:
            # 檢查 place_id 是否已存在，若已存在則不插入
            cursor.execute('''SELECT * FROM places WHERE place_id = ?''', (place.get('place_id'),))
            existing_place = cursor.fetchone()
            if existing_place is None:
                cursor.execute('''
                    INSERT OR IGNORE INTO places (name, address, rating, user_ratings_total, place_id, query)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    place.get('name'),
                    place.get('formatted_address', 'N/A'),
                    float(place.get('rating')) if place.get('rating') is not None else None,
                    int(place.get('user_ratings_total')) if place.get('user_ratings_total') is not None else None,
                    place.get('place_id'),
                    query  # 儲存查詢關鍵字
                ))
        except sqlite3.IntegrityError as e:
            print("資料庫插入錯誤:", e)
    conn.commit()
    conn.close()
    print("所有景點數據已成功儲存到資料庫中。")

# 主程式
def main():
    init_db()
    places = fetch_places(QUERY)
    if places:
        save_to_db(places, QUERY)  # 傳入查詢關鍵字
        print(f"成功存儲 {len(places)} 個資料到資料庫中！")
    else:
        print("未獲取到任何景點數據。")

if __name__ == '__main__':
    main()
