import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process

# Global variables (will be loaded later)
movies = None
genre_matrix = None


# ----------------------------
# LOAD DATASET + BUILD MODEL
# ----------------------------
def load_model():
    global movies, genre_matrix

    print("Loading movies dataset...")

    movies = pd.read_csv("data/movies.csv")

    print("Dataset loaded!")
    print("Total movies:", len(movies))

    # Clean genres
    movies["genres"] = movies["genres"].str.replace("|", " ", regex=False)

    print("Creating TF-IDF matrix...")

    tfidf = TfidfVectorizer()
    genre_matrix = tfidf.fit_transform(movies["genres"])

    print("TF-IDF matrix created!")


# ----------------------------
# FUZZY SEARCH FUNCTION
# ----------------------------
def find_closest_movie(user_input):

    titles = movies["title"].tolist()

    match, score, index = process.extractOne(
        user_input,
        titles
    )

    if score < 60:
        return None

    return match


# ----------------------------
# SINGLE MOVIE RECOMMENDATION
# ----------------------------
def recommend(movie_title, num_recommendations=10):

    try:
        movie_index = movies[movies["title"] == movie_title].index[0]
    except:
        return ["Movie not found"]

    similarity_scores = cosine_similarity(
        genre_matrix[movie_index],
        genre_matrix
    )

    similarity_scores = list(enumerate(similarity_scores[0]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    movie_indices = [
        i[0] for i in similarity_scores[1:num_recommendations + 1]
    ]

    return movies["title"].iloc[movie_indices].tolist()


# ----------------------------
# MULTI MOVIE TASTE RECOMMENDATION
# ----------------------------
def recommend_from_list(movie_list, num_recommendations=5):

    movie_indices = []

    for movie in movie_list:

        matched_movie = find_closest_movie(movie)

        if matched_movie is None:
            continue

        index = movies[movies["title"] == matched_movie].index[0]
        movie_indices.append(index)

    if len(movie_indices) == 0:
        return ["No valid movies found"]

    # Create user taste vector
    user_vector = genre_matrix[movie_indices].mean(axis=0)

    # Convert matrix to numpy array
    user_vector = user_vector.A

    similarity_scores = cosine_similarity(user_vector, genre_matrix)

    similarity_scores = list(enumerate(similarity_scores[0]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommended_indices = [
        i[0] for i in similarity_scores
        if i[0] not in movie_indices
    ][:num_recommendations]

    return movies["title"].iloc[recommended_indices].tolist()
