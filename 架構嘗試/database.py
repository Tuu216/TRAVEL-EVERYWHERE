import sqlite3
from config import DATABASE_NAME

def initialize_database():
    """清空並重新建立資料表結構。"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 建立資料表
    cursor.execute('DROP TABLE IF EXISTS places')
    cursor.execute('''
        CREATE TABLE places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_places(places):
    """儲存景點資料至資料庫。"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    for place in places:
        cursor.execute('''
            INSERT INTO places (name, address, rating, user_ratings_total, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (place["name"], place["address"], place["rating"], place["user_ratings_total"], str(place["tags"])))

    conn.commit()
    conn.close()

def query_places(min_rating=0, max_results=10):
    """查詢符合條件的景點資料。"""
    conn = sqlite3.connect(DATABASE_NAME)
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

    return [
        {
            "name": row[0],
            "address": row[1],
            "rating": row[2],
            "user_ratings_total": row[3],
            "tags": row[4]
        }
        for row in results
    ]
