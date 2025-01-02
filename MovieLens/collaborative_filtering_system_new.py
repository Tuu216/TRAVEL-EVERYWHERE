#%% 導入所需的庫
import numpy as np
import pandas as pd
from numpy import dot  # 引入點乘函數
from numpy.linalg import norm  # 引入歐幾里得範數計算函數

#%% 讀取數據
movies = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\movies.csv")  # 讀取電影數據
movies.drop(columns="genres", inplace=True)  # 刪除不必要的類別列
df = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\ratings.csv")  # 讀取評分數據
df.drop(columns="timestamp", inplace=True)  # 刪除不必要的時間戳列
df = pd.merge(df, movies, on='movieId')  # 合併評分和電影數據
print(df.head())  # 顯示合併後的數據的前幾行

#%% 定義常用函數

def cal_similarity_for_movie_ratings(user1, user2, movies_id, method="cosine"):
    """計算用戶1和用戶2之間的電影評分相似度
    
    Args:
        user1 (int): 用戶1的ID
        user2 (int): 用戶2的ID
        movies_id (list): 共同觀看的電影ID列表
        method (str): 使用的相似度計算方法，默認為 "cosine"
    
    Returns:
        float: 計算的相似度值
    """
    u1 = df[df["userId"] == user1]  # 獲取用戶1的評分數據
    u2 = df[df["userId"] == user2]  # 獲取用戶2的評分數據
    vec1 = u1[u1.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values  # 用戶1共同電影的評分
    vec2 = u2[u2.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values  # 用戶2共同電影的評分
    if method == "cosine":  # 如果選擇餘弦相似度
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))  # 返回餘弦相似度
    return None  # 如果方法不正確，返回空值

def find_common_movies(user1, user2):
    """查找兩位用戶共同觀看的電影
    
    Args:
        user1 (int): 用戶1的ID
        user2 (int): 用戶2的ID
    
    Returns:
        set: 兩位用戶共同觀看的電影ID集合
    """
    s1 = set((df.loc[df["userId"] == user1, "movieId"].values))  # 獲取用戶1觀看的電影ID
    s2 = set((df.loc[df["userId"] == user2, "movieId"].values))  # 獲取用戶2觀看的電影ID
    return s1.intersection(s2)  # 返回共同觀看的電影ID集合

def find_the_most_similar_users(user, num=10):
    """查找與指定用戶最相似的用戶
    
    Args:
        user (int): 用戶ID
        num (int): 查找的相似用戶數量，默認為10
    
    Returns:
        list: 相似用戶的ID列表
    """
    # 計算用戶與其他用戶之間的相似度
    similarities = []  # 相似度列表
    user_ids = []  # 用戶ID列表
    for other_user in df.userId.unique():  # 遍歷所有用戶
        if other_user == user:  # 跳過自己
            continue
        
        common_movies = find_common_movies(user, other_user)  # 查找共同觀看的電影
        
        if len(common_movies) < 10:  # 如果共同電影少於10部，則相似度為0
            sim = 0
        else:
            sim = cal_similarity_for_movie_ratings(user, other_user, common_movies)  # 計算相似度
        
        similarities.append(sim)  # 添加相似度
        user_ids.append(other_user)  # 添加其他用戶ID
            
    # 找到前-n個最相似的用戶
    similarities, user_ids = np.array(similarities), np.array(user_ids)  # 將相似度和用戶ID轉換為數組
    sorted_index = (np.argsort(similarities)[::-1][:num]).tolist()  # 按相似度排序，選擇前-n個
    most_similar_users = user_ids[sorted_index]  # 根據排序結果獲取用戶ID
    return most_similar_users  # 返回最相似用戶的ID

def recommend(user, similar_users, top_n=10):
    """根據最相似的用戶推薦電影
    
    Args:
        user (int): 用戶ID
        similar_users (list): 相似用戶的ID列表
        top_n (int): 返回的推薦電影數量，默認為10
    
    Returns:
        top_ratings (dataframe): 包含最推薦電影和平均評分的數據框
    """
    
    # 查找用戶尚未觀看而相似用戶觀看的電影
    seen_movies = np.unique(df.loc[df["userId"] == user, "movieId"].values)  # 獲取用戶已觀看的電影ID
    not_seen_cond = df["movieId"].isin(seen_movies) == False  # 確定用戶尚未觀看的電影
    similar_cond = df["userId"].isin(similar_users)  # 確定相似用戶的條件
    not_seen_movies_ratings = df[not_seen_cond & similar_cond][["movieId", "rating"]]  # 獲取未觀看電影的評分
    
    # 根據最相似的用戶的評分計算平均評分
    average_ratings = not_seen_movies_ratings.groupby("movieId").mean()  # 計算每部電影的平均評分
    average_ratings.reset_index(inplace=True)  # 重設索引
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]  # 按評分排序，選擇前-n部電影
    top_ratings.reset_index(inplace=True, drop=True)  # 重設索引，並丟棄舊索引
    return top_ratings  # 返回推薦的電影

#%%

num = 15  # 設定要查找的最相似用戶數量
top_n = 10  # 設定要推薦的電影數量
user_id = int(input("請輸入您的用戶ID: "))# 設定用戶ID
similar_users = find_the_most_similar_users(user_id, num)  # 查找與指定用戶最相似的用戶
top_ratings = recommend(user_id, similar_users, top_n)  # 根據相似用戶推薦電影

print(f"Top-{num} similar users: {similar_users}")  # 輸出最相似用戶的ID
print(f"Top-{top_n} average ratings by the most similar users:")  # 輸出推薦電影的平均評分
print(pd.merge(top_ratings, movies, on='movieId'))  # 合併推薦電影和電影信息，並顯示結果
