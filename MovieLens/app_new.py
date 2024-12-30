import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from numpy.linalg import norm
from flask import Flask, render_template, request

# Initialize Flask application
app = Flask(__name__)

# Load place and rating data
places = pd.read_csv('taichung_places_data.csv', sep=',').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
ratings = pd.read_csv('user_place_ratings_taichung.csv', sep=',').apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Ensure data types are correct
places['placeId'] = places['placeId'].astype(int)
ratings[['placeId', 'userId']] = ratings[['placeId', 'userId']].astype(int)

# Calculate vote count and average ratings
vote_count = ratings.groupby("placeId").count()["userId"].rename("vote_count").reset_index()
vote_average = ratings.groupby("placeId").mean()["rating"].rename("vote_average")

# Calculate global average rating and set minimum vote threshold
C = vote_average.mean()
m = vote_count["vote_count"].quantile(0.9)

# Filter places meeting the minimum vote threshold
q_places = vote_count[vote_count["vote_count"] >= m].reset_index(drop=True)
q_places = q_places.merge(vote_average, on="placeId")

# Weighted rating calculation
def weighted_rating(x, m=m, C=C):
    v = x["vote_count"]
    R = x["vote_average"]
    return (v / (v + m) * R) + (m / (m + v) * C)

q_places["score"] = q_places.apply(weighted_rating, axis=1)
q_places = q_places.sort_values('score', ascending=False)

# Merge with place details
df = q_places.merge(places, on='placeId')

# Generate a bar chart for popular places
def save_popular_places_plot():
    plt.figure(figsize=(10, 6))
    plt.barh(df['title'].head(6), df['score'].head(6), align='center', color='skyblue')
    plt.gca().invert_yaxis()
    plt.xlabel("Scores")
    plt.title("Popular Places")
    plt.tight_layout()
    plt.savefig('static/popular_places.png')
    plt.close()

save_popular_places_plot()

# Generate user and place vectors
place_rating = pd.merge(ratings[["userId", "placeId"]], places[["placeId", "genres"]], on='placeId')
dummies = place_rating["genres"].str.get_dummies('|')
user_vec = pd.concat([place_rating, dummies], axis=1)
user_vec.drop(['placeId', 'genres'], axis=1, inplace=True)
user_vec = user_vec.groupby("userId").mean()

dummies = places["genres"].str.get_dummies('|')
place_vec = pd.concat([places["placeId"], dummies], axis=1)
place_vec.set_index("placeId", inplace=True)

# Check shapes and columns
print("User Vector Shape:", user_vec.shape)
print("User Vector Columns:", user_vec.columns)
print("Place Vector Shape:", place_vec.shape)
print("Place Vector Columns:", place_vec.columns)

# Ensure same features
common_columns = user_vec.columns.intersection(place_vec.columns)
user_vec = user_vec[common_columns]
place_vec = place_vec[common_columns]

# Calculate user-place similarity matrix
user_place_similarity_matrix = pd.DataFrame(cosine_similarity(user_vec.values, place_vec.values), 
                                            index=user_vec.index, columns=place_vec.index)

# Find similar users
def find_similar_users(user_id, num=10):
    similarities = []
    for other_user in ratings['userId'].unique():
        if other_user == user_id:
            continue
        common_places = set(ratings[ratings['userId'] == user_id]['placeId']).intersection(
            ratings[ratings['userId'] == other_user]['placeId'])
        if len(common_places) < 10:
            similarities.append((other_user, 0))
            continue
        user_ratings = ratings[(ratings['userId'] == user_id) & (ratings['placeId'].isin(common_places))]["rating"].values
        other_ratings = ratings[(ratings['userId'] == other_user) & (ratings['placeId'].isin(common_places))]["rating"].values
        similarity = np.dot(user_ratings, other_ratings) / (norm(user_ratings) * norm(other_ratings))
        similarities.append((other_user, similarity))
    return sorted(similarities, key=lambda x: x[1], reverse=True)[:num]

# Recommend places
def recommend_places(user_id, similar_users, top_n=10):
    recommendations = []
    for place in ratings['placeId'].unique():
        if place in ratings[ratings['userId'] == user_id]['placeId'].values:
            continue
        users_ratings = ratings[(ratings['userId'].isin(similar_users)) & (ratings['placeId'] == place)]
        if users_ratings.empty:
            continue
        avg_rating = users_ratings['rating'].mean()
        recommendations.append((place, avg_rating))
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:top_n]
    return pd.DataFrame(recommendations, columns=['placeId', 'rating'])

@app.route('/')
def index():
    return render_template('index.html', recommended_places=None)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = int(request.form['user_id'])
    similar_users = [user[0] for user in find_similar_users(user_id, num=15)]
    top_ratings = recommend_places(user_id, similar_users, top_n=10)
    recommended_places = top_ratings.merge(places, on='placeId')
    return render_template('index.html', user_id=user_id, recommended_places=recommended_places.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)
