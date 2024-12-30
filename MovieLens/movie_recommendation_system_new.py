# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 15:28:46 2023

@author: Jerry
""" 

#%% 匯入所需的庫
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from numpy.linalg import norm

#%% 讀取數據
movies = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\movies.csv")  # 讀取電影數據
rating = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\ratings.csv")  # 讀取評分數據

#%% 計算每部電影的評分數量和平均評分
vote_count = rating.groupby("movieId").count()["userId"].rename("vote_count").reset_index()  # 計算每部電影的投票數
vote_average = rating.groupby("movieId").mean()["rating"]  # 計算每部電影的平均評分
C = vote_average.mean()  # 計算所有電影的平均評分

# 設置門檻值，選擇評分數量大於等於90%的電影
m = vote_count["vote_count"].quantile(0.9)  
q_movies = vote_count[vote_count["vote_count"] >= m].reset_index(drop=True)  # 選擇投票數量高的電影
q_movies["vote_average"] = vote_average[q_movies.movieId].values  # 將平均評分添加到數據框中

# 定義加權評分的計算函數
def weighted_rating(x, m=m, C=C):
    v = x["vote_count"]  # 取得投票數
    R = x["vote_average"]  # 取得平均評分
    # 根據 IMDB 的公式計算加權評分
    return (v/(v+m) * R) + (m/(m+v) * C)

# 計算每部電影的加權評分
q_movies["score"] = q_movies.apply(weighted_rating, axis=1).values  
# 根據加權評分對電影進行排序
q_movies = q_movies.sort_values('score', ascending=False)  

# 將選定的電影數據與電影信息進行合併
df = pd.merge(q_movies, movies, on='movieId')  
df.head()  # 顯示前幾行數據

# 繪製電影的加權評分條形圖
plt.barh(df['title'].head(6), df['score'].head(6), align='center', color='skyblue')
plt.gca().invert_yaxis()  # 反轉 y 軸，使最高分的電影在上面
plt.xlabel("Scores")
plt.title("Popular Movies")

#%% 繪製投票數和平均評分的散點圖
f, ax = plt.subplots(figsize=(6, 6))  # 設置圖形大小
sns.scatterplot(x="vote_count", y="vote_average", data=q_movies)  # 繪製散點圖
ax.set_ylabel("Vote average", fontsize=14)  # 設置 y 軸標籤
ax.set_xlabel("Vote count", fontsize=14)  # 設置 x 軸標籤

#%% 將電影類別轉換為虛擬變量（one-hot encoding）
genres = df.genres.str.get_dummies(sep="|")  # 將類別列分解為多個列
df = pd.merge(df, genres, left_index=True, right_index=True)  # 合併虛擬變量
df.drop("genres", axis=1, inplace=True)  # 刪除原類別列

#%% 顯示前幾部行動類型的電影
columns = ["title", "vote_count", "vote_average"]  # 設定要顯示的列
df.loc[df["Action"] == 1, columns].head()  # 顯示前幾部行動類型的電影

# 顯示前幾部喜劇類型的電影
df.loc[df["Comedy"] == 1, columns].head()  # 顯示前幾部喜劇類型的電影

#%% 基於內容的推薦系統

def get_the_most_similar_movies(user_id, user_movie_matrix, num):
    """查找與用戶最相似的前-n部電影"""
    user_vec = user_movie_matrix.loc[user_id].values  # 獲取用戶的電影向量
    sorted_index = np.argsort(user_vec)[::-1][:num]  # 排序並選擇前-n個最相似的電影
    return list(user_movie_matrix.columns[sorted_index])  # 返回電影ID列表
 
# 創建電影向量
dummies = movies["genres"].str.get_dummies('|')  # 將類別轉換為虛擬變量
movie_vec = pd.concat([movies["movieId"], dummies], axis=1)  # 合併電影ID和虛擬變量
movie_vec.set_index("movieId", inplace=True)  # 將電影ID設為索引

# 創建用戶向量
movie_rating = pd.merge(rating[["userId", "movieId"]], movies[["movieId", "genres"]], on='movieId')  # 合併評分和電影數據
dummies = movie_rating["genres"].str.get_dummies('|')  # 將類別轉換為虛擬變量
user_vec = pd.concat([movie_rating, dummies], axis=1)  # 合併用戶評分和虛擬變量
user_vec.drop(['movieId', 'genres'], axis=1, inplace=True)  # 刪除不需要的列
user_vec = user_vec.groupby("userId").mean()  # 計算每個用戶的平均評分

# 計算用戶與電影之間的相似度
user_movie_similarity_matrix = cosine_similarity(user_vec.values, movie_vec.values)  
user_movie_similarity_matrix = pd.DataFrame(user_movie_similarity_matrix, index=user_vec.index, columns=movie_vec.index)  

# 查找與用戶1最相似的前-10部電影
movied_ids = get_the_most_similar_movies(1, user_movie_similarity_matrix, 10)  
print(movies[movies["movieId"].isin(movied_ids)]["title"])  # 顯示電影標題

#%% 基於協同過濾的推薦系統

def find_common_movies(user1, user2):
    """查找兩位用戶共同觀看的電影"""
    s1 = set((df.loc[df["userId"] == user1, "movieId"].values))  # 用戶1觀看的電影ID
    s2 = set((df.loc[df["userId"] == user2, "movieId"].values))  # 用戶2觀看的電影ID
    return s1.intersection(s2)  # 返回兩位用戶共同觀看的電影ID

def cal_similarity_for_movie_ratings(user1, user2, movies_id, method="cosine"):
    """計算用戶1和用戶2之間的電影評分相似度"""
    u1 = df[df["userId"] == user1]  # 獲取用戶1的評分數據
    u2 = df[df["userId"] == user2]  # 獲取用戶2的評分數據
    vec1 = u1[u1.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values  # 用戶1共同電影的評分
    vec2 = u2[u2.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values  # 用戶2共同電影的評分
    if method == "cosine":        
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))  # 計算餘弦相似度
    return None

def find_the_most_similar_users(user, num=10):
    """查找最相似的用戶"""
    similarities = []  # 相似度列表
    user_ids = []  # 用戶ID列表
    for other_user in df.userId.unique():
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
    similarities, user_ids = np.array(similarities), np.array(user_ids)  
    sorted_index = (np.argsort(similarities)[::-1][:num]).tolist()  # 排序並獲取最相似的用戶
    most_similar_users = user_ids[sorted_index]  # 返回最相似用戶的ID
    return most_similar_users

def recommend(user, similar_users, top_n=10):
    """根據最相似用戶推薦電影"""
    seen_movies = np.unique(df.loc[df["userId"] == user, "movieId"].values)  # 獲取用戶已觀看的電影ID
    not_seen_cond = df["movieId"].isin(seen_movies) == False  # 篩選未觀看的電影
    similar_cond = df["userId"].isin(similar_users)  # 篩選相似用戶的電影
    not_seen_movies_ratings = df[not_seen_cond & similar_cond][["movieId", "rating"]]  # 獲取未觀看電影的評分
    
    # 計算相似用戶對未觀看電影的平均評分
    average_ratings = not_seen_movies_ratings.groupby("movieId").mean()  
    average_ratings.reset_index(inplace=True)  # 重置索引
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]  # 獲取最高評分的電影
    top_ratings.reset_index(inplace=True, drop=True)  # 重置索引
    return top_ratings

# 整合用戶評分和電影數據
movie_rating = pd.merge(rating[["userId", "movieId", "rating"]], movies[["movieId", "genres"]], on='movieId')  
dummies = movie_rating["genres"].str.get_dummies('|')  # 將類別轉換為虛擬變量
df = pd.concat([movie_rating, dummies], axis=1)  # 合併數據
df.drop(['genres'], axis=1, inplace=True)  # 刪除原類別列

num = 15  # 要查找的相似用戶數量
top_n = 10  # 要推薦的電影數量
user_id = 1  # 設定用戶ID
similar_users = find_the_most_similar_users(user_id, num)  # 查找最相似的用戶
top_ratings = recommend(user_id, similar_users, top_n)  # 獲取推薦電影

# 打印最相似的用戶和推薦的電影
print(f"Top-{num} similar users: {similar_users}")  
print(f"Top-{top_n} average ratings by the most similar users:")
print(pd.merge(top_ratings, movies, on='movieId'))  # 顯示推薦的電影及其信息
