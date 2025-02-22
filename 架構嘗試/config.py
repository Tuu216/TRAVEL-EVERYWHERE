import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# API 和資料庫設定
API_KEY = os.getenv("GOOGLE_API_KEY")
print('api:',API_KEY)
if not API_KEY:
    raise ValueError("找不到 GOOGLE_API_KEY 環境變數")
DATABASE_NAME = "places.db"

# 地點類型對照表
TYPE_TO_CATEGORY = {
    "tourist_attraction": ("藝術人文", "古蹟"),
    "museum": ("藝術人文", "展覽"),
    "park": ("運動休閒", "自然景觀"),
    "natural_feature": ("運動休閒", "自然景觀"),
    "amusement_park": ("娛樂遊玩", "主題樂園"),
    "zoo": ("娛樂遊玩", "動物園"),
    "aquarium": ("娛樂遊玩", "水族館"),
    "restaurant": ("吃貨天堂", "餐廳"),
    "cafe": ("吃貨天堂", "飲料冰品"),
    "bar": ("吃貨天堂", "飲料冰品"),
    "casino": ("娛樂遊玩", "賭場"),
    "shopping_mall": ("娛樂遊玩", "購物中心"),
    "night_club": ("娛樂遊玩", "夜生活"),
    "church": ("藝術人文", "宗教"),
    "hindu_temple": ("藝術人文", "宗教"),
    "mosque": ("藝術人文", "宗教"),
    "synagogue": ("藝術人文", "宗教"),
    "spa": ("運動休閒", "休閒養生"),
    "gym": ("運動休閒", "健身"),
    "stadium": ("運動休閒", "體育場"),
    "food": ("吃貨天堂", "小吃"),
    "lodging": ("運動休閒", "休閒養生"),
    "art_gallery": ("藝術人文", "展覽"),
    "landmark": ("藝術人文", "古蹟")
}
