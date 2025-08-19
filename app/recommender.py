import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset once (efficient)
df = pd.read_csv("tmdb_dataset.csv")

def combine_features(row):
    genres = " ".join(row['genres'])
    keywords = " ".join(row['keywords'])
    spoken = " ".join(row['spoken_languages'])
    return f"{str(row['overview'])} {str(row['tagline'])} {genres} {keywords} {spoken}"

df['tags'] = df.apply(combine_features, axis=1)

# Vectorization
tfidf = TfidfVectorizer(stop_words="english", max_features=10000)
tfidf_matrix = tfidf.fit_transform(df['tags'].fillna(""))

# ---------------------------
# Recommendation function
# ---------------------------
def recommend_movies(fav_genres, fav_languages, top_n=20):
    filtered_df = df[
        df['genres'].apply(lambda g: any(genre in g for genre in fav_genres)) &
        df['spoken_languages'].apply(lambda l: any(lang in l for lang in fav_languages))
    ]
    if filtered_df.empty:
        return pd.DataFrame()
    
    user_profile = " ".join(fav_genres + fav_languages)
    user_vec = tfidf.transform([user_profile])
    
    filtered_idx = filtered_df.index
    cosine_scores = cosine_similarity(user_vec, tfidf_matrix[filtered_idx]).flatten()
    
    filtered_df = filtered_df.copy()
    filtered_df['similarity'] = cosine_scores
    
    recommended = filtered_df.sort_values(
        by=['similarity', 'vote_average', 'vote_count', 'popularity'],
        ascending=False
    ).head(top_n)
    
    return recommended['imdb_id'].tolist()
