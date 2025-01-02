import sqlite3
from datetime import datetime
from typing import List, Dict
import json

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                DROP TABLE IF EXISTS places;
                DROP TABLE IF EXISTS place_types;
                
                CREATE TABLE places (
                    id INTEGER PRIMARY KEY,
                    place_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    address TEXT,
                    lat REAL,
                    lng REAL,
                    rating REAL,
                    user_ratings_total INTEGER,
                    price_level INTEGER,
                    created_at TIMESTAMP
                );

                CREATE TABLE place_types (
                    id INTEGER PRIMARY KEY,
                    place_id INTEGER,
                    type_name TEXT,
                    tag_level1 TEXT,
                    tag_level2 TEXT,
                    FOREIGN KEY(place_id) REFERENCES places(id)
                );
            ''')

    def save_places(self, places: List[Dict]):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            for place in places:
                cursor.execute('''
                    INSERT INTO places (
                        place_id, name, address, lat, lng,
                        rating, user_ratings_total, price_level, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    place['place_id'],
                    place['name'],
                    place['address'],
                    place['location']['lat'],
                    place['location']['lng'],
                    place.get('rating'),
                    place.get('user_ratings_total'),
                    place.get('price_level'),
                    datetime.now()
                ))
                
                place_id = cursor.lastrowid
                for tag in place['tags']:
                    cursor.execute('''
                        INSERT INTO place_types (place_id, type_name, tag_level1, tag_level2)
                        VALUES (?, ?, ?, ?)
                    ''', (place_id, tag[0], tag[1], tag[2]))

    def get_filtered_places(self, min_rating: float = 0, max_results: int = 10) -> List[Dict]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, GROUP_CONCAT(pt.tag_level1 || ',' || pt.tag_level2, ';') as tags
                FROM places p
                LEFT JOIN place_types pt ON p.id = pt.place_id
                WHERE p.rating >= ?
                GROUP BY p.id
                ORDER BY p.rating DESC, p.user_ratings_total DESC
                LIMIT ?
            ''', (min_rating, max_results))
            
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                place_dict = dict(zip(columns, row))
                if place_dict['tags']:
                    tags = [tuple(tag.split(',')) for tag in place_dict['tags'].split(';')]
                    place_dict['tags'] = tags
                else:
                    place_dict['tags'] = []
                results.append(place_dict)
            return results
