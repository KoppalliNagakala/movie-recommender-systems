import pickle
import streamlit as st
import requests
import pandas as pd
import time

def fetch_poster(movie_id, retries=3, delay=2, timeout=5):
    """Fetches the movie poster URL with retries and timeout."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                return full_path
            else:
                st.error(f"No poster path found for movie ID {movie_id}")
                return None
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:  # Retry if not the last attempt
                time.sleep(delay)  # Delay before retrying
            else:
                # st.error(f"Error fetching poster after {retries} attempts: {e}")
                return None
        except requests.exceptions.Timeout as e:
            st.error(f"Timeout occurred: {e}")
            return None

    return None  # Fallback in case all attempts fail

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')
movies_dict = pickle.load(open('models/movie_dict.pkl', 'rb'))
similarity = pickle.load(open('models/similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for idx, col in enumerate(cols):
        with col:
            st.text(recommended_movie_names[idx])
            if recommended_movie_posters[idx]:
                st.image(recommended_movie_posters[idx])
            else:
                st.text("Poster not found, try again later")
