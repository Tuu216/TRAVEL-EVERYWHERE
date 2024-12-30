import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from flask import Flask, render_template, request
from numpy.linalg import norm

app = Flask(__name__)

# 讀取資料
movies = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\movies.csv")  # 讀取電影數據
ratings = pd.read_csv(r"C:\Users\MSiPC\Downloads\MovieLens\ratings.csv")

# 計算評分
vote_count = ratings.groupby("movieId").count()["userId"].rename("vote_count").reset_index()
vote_average = ratings.groupby("movieId").mean()["rating"]
C = vote_average.mean()

m = vote_count["vote_count"].quantile(0.9)
q_movies = vote_count[vote_count["vote_count"] >= m].reset_index(drop=True)
q_movies["vote_average"] = vote_average[q_movies.movieId].values

def weighted_rating(x, m=m, C=C):
    v = x["vote_count"]
    R = x["vote_average"]
    return (v / (v + m) * R) + (m / (m + v) * C)

q_movies["score"] = q_movies.apply(weighted_rating, axis=1).values
q_movies = q_movies.sort_values('score', ascending=False)

df = pd.merge(q_movies, movies, on='movieId')

# 生成流行電影的圖表
def save_popular_movies_plot():
    plt.figure(figsize=(10, 6))  # 增加圖片的大小
    plt.barh(df['title'].head(6), df['score'].head(6), align='center', color='skyblue')
    plt.gca().invert_yaxis()
    plt.xlabel("Scores")
    plt.title("Popular Movies")
    plt.xticks(rotation=45)  # 如果有必要，旋轉 x 軸標籤
    plt.tight_layout()  # 自動調整子圖參數，使之適應整個圖像區域
    plt.savefig('static/popular_movies.png')  # 儲存為圖片
    plt.close()


save_popular_movies_plot()

# 使用者-電影相似度
def get_the_most_similar_movies(user_id, user_movie_matrix, num):
    user_vec = user_movie_matrix.loc[user_id].values
    sorted_index = np.argsort(user_vec)[::-1][:num]
    return list(user_movie_matrix.columns[sorted_index])

# 生成電影向量
dummies = movies["genres"].str.get_dummies('|')
movie_vec = pd.concat([movies["movieId"], dummies], axis=1)
movie_vec.set_index("movieId", inplace=True)

# 生成使用者向量
movie_rating = pd.merge(ratings[["userId", "movieId"]], movies[["movieId", "genres"]], on='movieId')
dummies = movie_rating["genres"].str.get_dummies('|')
user_vec = pd.concat([movie_rating, dummies], axis=1)
user_vec.drop(['movieId', 'genres'], axis=1, inplace=True)
user_vec = user_vec.groupby("userId").mean()

user_movie_similarity_matrix = cosine_similarity(user_vec.values, movie_vec.values)
user_movie_similarity_matrix = pd.DataFrame(user_movie_similarity_matrix, index=user_vec.index, columns=movie_vec.index)

@app.route('/')
def index():
    # 定義 recommended_movies 為 None
    recommended_movies = None
    return render_template('index.html', recommended_movies=recommended_movies)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    user_id = int(request.form['user_id'])
    num = 15
    top_n = 10
    similar_users = find_the_most_similar_users(user_id, num)
    top_ratings = recommend(user_id, similar_users, top_n)

    recommended_movies = pd.merge(top_ratings, movies, on='movieId')
    return render_template('index.html', user_id=user_id, recommended_movies=recommended_movies)

def find_common_movies(user1, user2):
    s1 = set((ratings.loc[ratings["userId"] == user1, "movieId"].values))
    s2 = set((ratings.loc[ratings["userId"] == user2, "movieId"].values))
    return s1.intersection(s2)

def cal_similarity_for_movie_ratings(user1, user2, movies_id, method="cosine"):
    u1 = ratings[ratings["userId"] == user1]
    u2 = ratings[ratings["userId"] == user2]
    vec1 = u1[u1.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values
    vec2 = u2[u2.movieId.isin(movies_id)].sort_values(by="movieId")["rating"].values
    if method == "cosine":
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    return None

def find_the_most_similar_users(user, num=10):
    similarities = []
    user_ids = []
    for other_user in ratings["userId"].unique():
        if other_user == user:
            continue
        common_movies = find_common_movies(user, other_user)
        if len(common_movies) < 10:
            sim = 0
        else:
            sim = cal_similarity_for_movie_ratings(user, other_user, common_movies)
        similarities.append(sim)
        user_ids.append(other_user)
    
    similarities, user_ids = np.array(similarities), np.array(user_ids)
    sorted_index = (np.argsort(similarities)[::-1][:num]).tolist()
    most_similar_users = user_ids[sorted_index] 
    return most_similar_users

def recommend(user, similar_users, top_n=10):
    seen_movies = np.unique(ratings.loc[ratings["userId"] == user, "movieId"].values)
    not_seen_cond = ratings["movieId"].isin(seen_movies) == False
    similar_cond = ratings["userId"].isin(similar_users)
    not_seen_movies_ratings = ratings[not_seen_cond & similar_cond][["movieId", "rating"]]
    
    average_ratings = not_seen_movies_ratings.groupby("movieId").mean()
    average_ratings.reset_index(inplace=True)
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]
    top_ratings.reset_index(inplace=True, drop=True)
    return top_ratings


if __name__ == '__main__':
    app.run(debug=True)

