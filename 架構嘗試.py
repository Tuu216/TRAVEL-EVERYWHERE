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

def main():
    API_KEY = "AIzaSyBrNGZNFHQfvy9zMTjmDNfNu9Pah1aP5eI"
    location = "25.0330,121.5654"  # Example: Taipei 101
    radius = 1000  # 1 km radius
    place_type = "tourist_attraction"  # Example: tourist attractions

    try:
        places = fetch_google_places(API_KEY, location, radius, place_type)
        print("Fetched Places:")
        for idx, place in enumerate(places, start=1):
            print(f"{idx}. {place['name']}")
            print(f"   Address: {place['address']}")
            print(f"   Rating: {place['rating']} ({place['user_ratings_total']} reviews)")
            print("----------------------------------")

        save_to_database(places)
        print("\nData saved to database successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
