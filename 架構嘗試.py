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
        places.append({
            "name": result.get("name"),
            "address": result.get("vicinity"),
            "rating": result.get("rating"),
            "user_ratings_total": result.get("user_ratings_total"),
        })

    return places

def save_to_database(places):
    """
    Save fetched places to SQLite database.

    Parameters:
    - places (list of dict): List of places with details to save.
    """
    conn = sqlite3.connect("places.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER
        )
    ''')

    # Insert data into the table
    for place in places:
        cursor.execute('''
            INSERT INTO places (name, address, rating, user_ratings_total)
            VALUES (?, ?, ?, ?)
        ''', (place["name"], place["address"], place["rating"], place["user_ratings_total"]))

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
        SELECT name, address, rating, user_ratings_total
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
            "user_ratings_total": row[3]
        } for row in results
    ]

    return filtered_places

def main():
    API_KEY = "AIzaSyBrNGZNFHQfvy9zMTjmDNfNu9Pah1aP5eI"
    location = "25.0330,121.5654"  # Example: Taipei 101
    radius = 1000  # 1 km radius
    place_type = "tourist_attraction"  # Example: tourist attractions

    try:
        # Fetch and save places
        places = fetch_google_places(API_KEY, location, radius, place_type)
        save_to_database(places)

        # Filter and display places
        min_rating = 4.0
        print(f"\nPlaces with rating >= {min_rating}:")
        filtered_places = filter_places(min_rating)
        for idx, place in enumerate(filtered_places, start=1):
            print(f"{idx}. {place['name']}")
            print(f"   Address: {place['address']}")
            print(f"   Rating: {place['rating']} ({place['user_ratings_total']} reviews)")
            print("----------------------------------")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
