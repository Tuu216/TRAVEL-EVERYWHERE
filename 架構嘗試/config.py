import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "API_KEY": os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE"),
    "DB_NAME": "places.db",
    "PLACE_TYPES": {
        "1": ("tourist_attraction", "景點"),
        "2": ("restaurant", "餐廳"),
        "3": ("museum", "博物館"),
        "4": ("park", "公園"),
        "5": ("shopping_mall", "購物中心")
    },
    "DEFAULT_RADIUS": 1000,
    "MAX_RESULTS": 10
}
