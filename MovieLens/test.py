#%% 匯入所需的庫
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

#%% 讀取數據
taichung_places = pd.read_csv('taichung_places_data.csv')  # 讀取台中景點數據
user_ratings = pd.read_csv('user_place_ratings_taichung.csv')  # 讀取用戶評分數據

#%% 計算每個景點的評分數量和平均評分
vote_count = user_ratings.groupby("placeId").count()["userId"].rename("vote_count").reset_index()
vote_average = user_ratings.groupby("placeId").mean()["rating"]
C = vote_average.mean()

# 設置門檻值，選擇評分數量大於等於90%的景點
m = vote_count["vote_count"].quantile(0.9)
q_places = vote_count[vote_count["vote_count"] >= m].reset_index(drop=True)
q_places["vote_average"] = vote_average[q_places.placeId].values

# 定義加權評分的計算函數
def weighted_rating(x, m=m, C=C):
    v = x["vote_count"]
    R = x["vote_average"]
    return (v/(v+m) * R) + (m/(m+v) * C)

q_places["score"] = q_places.apply(weighted_rating, axis=1).values
q_places = q_places.sort_values('score', ascending=False)

# 將選定的景點數據與景點信息進行合併
df = pd.merge(q_places, taichung_places, on='placeId')

#%% 基於內容的推薦系統
def get_the_most_similar_places(user_id, user_vec, place_similarity_matrix, top_n):
    """查找與用戶最相似的前-n個景點"""
    user_vector = user_vec.loc[user_id].values  # 獲取用戶的景點向量
    similarity_scores = place_similarity_matrix @ user_vector
    sorted_indices = np.argsort(similarity_scores)[::-1][:top_n]
    return list(place_similarity_matrix.index[sorted_indices])

# 創建景點向量
dummies = taichung_places["tags"].str.get_dummies('|')  # 將標籤轉換為虛擬變量
place_vec = pd.concat([taichung_places["placeId"], dummies], axis=1)
place_vec.set_index("placeId", inplace=True)

# 創建用戶向量
user_vec = user_ratings.pivot_table(index='userId', columns='placeId', values='rating').fillna(0)

# 確保 place_vec 和 user_vec 維度一致
place_vec = place_vec.reindex(columns=user_vec.columns, fill_value=0)

# 計算景點之間的相似度
place_similarity_matrix = cosine_similarity(place_vec.values)
place_similarity_matrix = pd.DataFrame(place_similarity_matrix, index=place_vec.index, columns=place_vec.index)

# 查找與用戶最相似的前10個景點
place_ids = get_the_most_similar_places(1, user_vec, place_similarity_matrix, 10)
print("基於內容推薦的景點:")
print(taichung_places[taichung_places["placeId"].isin(place_ids)]["title"])

#%% 基於協同過濾的推薦系統
def find_common_places(user1, user2):
    """查找兩位用戶共同評分的景點"""
    s1 = set(user_ratings.loc[user_ratings["userId"] == user1, "placeId"].values)  # 用戶1評分的景點ID
    s2 = set(user_ratings.loc[user_ratings["userId"] == user2, "placeId"].values)  # 用戶2評分的景點ID
    return s1.intersection(s2)  # 返回共同評分的景點ID

def recommend(user, similar_users, top_n=10):
    """根據最相似用戶推薦景點"""
    seen_places = np.unique(user_ratings.loc[user_ratings["userId"] == user, "placeId"].values)  # 已評分的景點ID
    not_seen_cond = ~user_ratings["placeId"].isin(seen_places)  # 篩選未評分的景點
    similar_cond = user_ratings["userId"].isin(similar_users)  # 篩選相似用戶的評分
    not_seen_places_ratings = user_ratings[not_seen_cond & similar_cond][["placeId", "rating"]]  # 未評分景點的評分

    # 計算相似用戶對未評分景點的平均評分
    average_ratings = not_seen_places_ratings.groupby("placeId").mean()
    average_ratings.reset_index(inplace=True)
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]
    top_ratings.reset_index(inplace=True, drop=True)
    return top_ratings

def find_the_most_similar_users(user_id, num=10):
    """根據用戶評分矩陣查找最相似的用戶"""
    # 獲取用戶評分向量
    user_vector = user_vec.loc[user_id].values.reshape(1, -1)
    # 計算用戶之間的相似度
    similarity_scores = cosine_similarity(user_vec.values, user_vector)
    # 取得與目標用戶最相似的前n個用戶
    similar_users_idx = np.argsort(similarity_scores.flatten())[::-1][1:num+1]
    return user_vec.index[similar_users_idx].tolist()

# 查找與用戶最相似的用戶並推薦景點
try:
    user_id = int(input("請輸入您的用戶ID: "))
    similar_users = find_the_most_similar_users(user_id, num=10)
    top_ratings = recommend(user_id, similar_users, top_n=5)

    # 打印推薦的景點
    print("基於協同過濾推薦的景點:")
    print(pd.merge(top_ratings, taichung_places, on="placeId"))
    print(f"與您最相似的用戶: {similar_users}")

except ValueError:
    print("請輸入有效的用戶ID！")