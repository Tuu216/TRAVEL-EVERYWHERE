from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 初始化 Flask 應用
app = Flask(__name__)

# 讀取數據
taichung_places = pd.read_csv('taichung_places_data.csv')
user_ratings = pd.read_csv('user_place_ratings_taichung.csv')

# 創建用戶評分矩陣
user_vec = user_ratings.pivot_table(index='userId', columns='placeId', values='rating').fillna(0)

# 定義推薦系統方法
def recommend(user, similar_users, top_n=10):
    seen_places = np.unique(user_ratings.loc[user_ratings["userId"] == user, "placeId"].values)
    not_seen_cond = ~user_ratings["placeId"].isin(seen_places)
    similar_cond = user_ratings["userId"].isin(similar_users)
    not_seen_places_ratings = user_ratings[not_seen_cond & similar_cond][["placeId", "rating"]]

    average_ratings = not_seen_places_ratings.groupby("placeId").mean()
    average_ratings.reset_index(inplace=True)
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]
    top_ratings.reset_index(inplace=True, drop=True)
    top_ratings = pd.merge(top_ratings, taichung_places, on="placeId")
    return top_ratings

def find_the_most_similar_users(user_id, num=10):
    user_vector = user_vec.loc[user_id].values.reshape(1, -1)
    similarity_scores = cosine_similarity(user_vec.values, user_vector)
    similar_users_idx = np.argsort(similarity_scores.flatten())[::-1][1:num+1]
    return user_vec.index[similar_users_idx].tolist()

# 路由設置
@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    similar_users = []
    error = None

    if request.method == 'POST':
        try:
            user_id = int(request.form['user_id'])
            if user_id not in user_vec.index:
                raise ValueError("用戶ID不存在！")

            similar_users = find_the_most_similar_users(user_id, num=10)
            top_ratings = recommend(user_id, similar_users, top_n=5)
            recommendations = top_ratings.to_dict(orient='records')
        except ValueError as e:
            error = str(e)

    return render_template('trymyself.html', recommendations=recommendations, similar_users=similar_users, error=error)

if __name__ == '__main__':
    app.run(debug=True)