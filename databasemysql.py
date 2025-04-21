import requests
import mysql.connector
import time
import os
from mysql.connector import Error

# API 設定
API_KEY = 'AIzaSyAU35K8XohOeEW7u8tiXfi3hwi5hzFCaCY'
BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'
QUERY = '台北小吃'

# MySQL 資料庫設定
DB_CONFIG = {
    'host': 'localhost',
    'user': '1021',  # 替換為你的 MySQL 用戶名
    'password': '@wwHew2qnndbnrj',  # 替換為你的 MySQL 密碼
    'database': 'place2'  # 替換為你的資料庫名稱
}


# 建立 MySQL 資料庫連接並創建表格
def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                address TEXT,
                rating FLOAT,
                user_ratings_total INT,
                place_id VARCHAR(255) UNIQUE,
                types TEXT,
                business_status VARCHAR(255),
                latitude FLOAT,
                longitude FLOAT,
                price_level INT,
                phone_number VARCHAR(255),
                opening_hours TEXT,
                photo_url TEXT,  -- 圖片 URL 欄位
                query VARCHAR(255)
            )
        ''')
        conn.commit()
        print("資料表創建成功或已存在")
    except Error as e:
        print(f"資料庫錯誤: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
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


# 獲取景點詳細資料
def fetch_place_details(place_id):
    params = {
        'place_id': place_id,
        'key': API_KEY,
        'fields': 'formatted_phone_number,opening_hours'
    }
    response = requests.get(DETAILS_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        result = data.get('result', {})
        return {
            'phone_number': result.get('formatted_phone_number', 'N/A'),
            'opening_hours': ', '.join(result.get('opening_hours', {}).get('weekday_text', [])) if result.get('opening_hours') else 'N/A'
        }
    return {'phone_number': 'N/A', 'opening_hours': 'N/A'}


# 獲取圖片 URL
def fetch_photo_url(photo_reference):
    if not photo_reference:
        return None
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_reference}&key={API_KEY}"


# 下載圖片到本地
def download_photo(photo_url, place_id):
    if not photo_url:
        return
    response = requests.get(photo_url, stream=True)
    if response.status_code == 200:
        os.makedirs("photos", exist_ok=True)
        file_path = f"photos/{place_id}.jpg"
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"圖片已下載: {file_path}")
    else:
        print(f"下載圖片失敗: {photo_url}")


# 儲存景點資料到資料庫
def save_to_db(places, query):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for place in places:
            try:
                # 檢查 place_id 是否已存在
                cursor.execute('''SELECT * FROM places WHERE place_id = %s''', (place.get('place_id'),))
                existing_place = cursor.fetchone()
                
                if existing_place is None:
                    # 獲取詳細資料
                    details = fetch_place_details(place.get('place_id'))
                    
                    # 獲取圖片 URL
                    photo_reference = place.get('photos', [{}])[0].get('photo_reference', None)
                    photo_url = fetch_photo_url(photo_reference)
                    
                    # 儲存圖片到本地
                    download_photo(photo_url, place.get('place_id'))
                    
                    # 插入資料
                    cursor.execute('''
                        INSERT INTO places (
                            name, address, rating, user_ratings_total, place_id,
                            types, business_status, latitude, longitude, price_level,
                            phone_number, opening_hours, photo_url, query
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        place.get('name'),
                        place.get('formatted_address', 'N/A'),
                        float(place.get('rating')) if place.get('rating') is not None else None,
                        int(place.get('user_ratings_total')) if place.get('user_ratings_total') is not None else None,
                        place.get('place_id'),
                        ', '.join(place.get('types', [])) if 'types' in place else 'N/A',
                        place.get('business_status', 'N/A'),
                        place['geometry']['location']['lat'] if 'geometry' in place else None,
                        place['geometry']['location']['lng'] if 'geometry' in place else None,
                        place.get('price_level') if 'price_level' in place else None,
                        details['phone_number'],
                        details['opening_hours'],
                        photo_url,
                        query
                    ))
                    print(f"已插入: {place.get('name')}")
            except mysql.connector.Error as e:
                print(f"插入資料時發生錯誤: {e}")
                conn.rollback()  # 回滾當前事務
            except Exception as e:
                print(f"發生錯誤: {e}")
        
        conn.commit()
        print("所有景點數據已成功儲存到資料庫中。")
    except Error as e:
        print(f"資料庫連接錯誤: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# 主程式
def main():
    init_db()
    places = fetch_places(QUERY)
    if places:
        save_to_db(places, QUERY)
        print(f"成功存儲 {len(places)} 個資料到資料庫中！")
    else:
        print("未獲取到任何景點數據。")


if __name__ == '__main__':
    main()
