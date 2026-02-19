import streamlit as st
import load_data
import requests
import time

TMDB_API_KEY = "762c7bacc7002081a82d1a76b5443c01"

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommendation System")
st.write("Get movie recommendations based on your taste.")


# ----------------------------
# LOAD MODEL (Cached)
# ----------------------------
@st.cache_resource
def initialize():
    load_data.load_model()
    return True

initialize()


# ----------------------------
# FETCH POSTER FROM TMDB
# ----------------------------
import time

import re
import time

@st.cache_data(show_spinner=False)
def fetch_poster(movie_title):
    url = "https://api.themoviedb.org/3/search/movie"

    # Remove year
    clean_title = re.sub(r"\(\d{4}\)", "", movie_title).strip()

    params = {
        "api_key": TMDB_API_KEY,
        "query": clean_title
    }

    try:
        time.sleep(0.6)  # 🔥 slower = safer

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception:
        return None

    return None




# ----------------------------
# USER INPUT
# ----------------------------
user_input = st.text_input(
    "Enter movie names separated by comma",
    placeholder="e.g. dark knight, inception, interstellar"
)


# ----------------------------
# RECOMMEND BUTTON
# ----------------------------
if st.button("Recommend"):

    if user_input.strip() == "":
        st.warning("Please enter at least one movie.")
    else:
        movie_list = [movie.strip() for movie in user_input.split(",")]

        try:
            recommendations = load_data.recommend_from_list(movie_list)
        except Exception as e:
            st.error(f"Model Error: {e}")
            recommendations = None

        # 🔥 SAFE CHECK
        if not recommendations:
            st.error("No recommendations found.")
        else:
            st.subheader("Recommended Movies")

            # Limit to 5 recommendations safely
            recommendations = recommendations[:5]

            cols = st.columns(5)

            for index, movie in enumerate(recommendations):
                poster_url = fetch_poster(movie)

                with cols[index % 5]:
                    if poster_url:
                        st.image(poster_url, use_container_width=True)
                    else:
                        st.write("Poster not found")
                    st.caption(movie)
