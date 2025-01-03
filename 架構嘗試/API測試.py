import requests

api_key = "AIzaSyCsgsowULrtmL8nhlQWtwvUoxRj4jI0aZw"
test_url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {
    "address": "台北市",
    "key": api_key
}

response = requests.get(test_url, params=params)
print(response.json())