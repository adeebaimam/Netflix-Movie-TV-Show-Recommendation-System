import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie

# Your TMDb API Key (replace with your own)
TMDB_API_KEY = '***'  # Replace with your own key
TMDB_API_URL = "https://api.themoviedb.org/3"

# Function to load Lottie animation from a URL or file
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Function to fetch IMDb ratings from TMDb
def get_imdb_rating(tmdb_id):
    movie_url = f"{TMDB_API_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    tv_url = f"{TMDB_API_URL}/tv/{tmdb_id}?api_key={TMDB_API_KEY}"
    
    movie_response = requests.get(movie_url)
    tv_response = requests.get(tv_url)
    
    # Check if the content is a movie or show
    if movie_response.status_code == 200:
        movie_data = movie_response.json()
        return movie_data.get('imdb_id', None)  # Return IMDb ID for the movie
    elif tv_response.status_code == 200:
        tv_data = tv_response.json()
        return tv_data.get('imdb_id', None)  # Return IMDb ID for the show
    return None

# Function to fetch genres from TMDb
def get_tmdb_genres():
    genres_url = f"{TMDB_API_URL}/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(genres_url)
    genre_data = response.json()
    return genre_data['genres']

# Function to get the genre ID from the genre name
def get_genre_id(genre_name):
    genres = get_tmdb_genres()  # Fetch genres from TMDb API
    for genre in genres:
        if genre['name'].lower() == genre_name.lower():
            return genre['id']
    return None  # Return None if no match is found

# Function to fetch trending movies and TV shows from TMDb with filters
def get_tmdb_trending(genre_id=None):
    trending_movies_url = f"{TMDB_API_URL}/trending/movie/week?api_key={TMDB_API_KEY}"
    trending_shows_url = f"{TMDB_API_URL}/trending/tv/week?api_key={TMDB_API_KEY}"
    
    # Apply filters if any
    if genre_id:
        trending_movies_url += f"&with_genres={genre_id}"
        trending_shows_url += f"&with_genres={genre_id}"
    
    # Fetch data from TMDb API
    response_movies = requests.get(trending_movies_url)
    response_shows = requests.get(trending_shows_url)
    
    trending_movies = response_movies.json()['results']
    trending_shows = response_shows.json()['results']
    
    # Combine trending movies and shows
    all_trending = []
    for movie in trending_movies[:10]:  # Limit to top 10 for example
        imdb_id = get_imdb_rating(movie['id'])
        all_trending.append({
            'title': movie['title'],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
            'netflix_url': f"https://www.netflix.com/search?q={movie['title'].replace(' ', '%20')}",
            'imdb_id': imdb_id,
            'imdb_rating': movie.get('vote_average', 'N/A')
        })
    
    for show in trending_shows[:10]:  # Limit to top 10 for example
        imdb_id = get_imdb_rating(show['id'])
        all_trending.append({
            'title': show['name'],
            'poster_url': f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show['poster_path'] else None,
            'netflix_url': f"https://www.netflix.com/search?q={show['name'].replace(' ', '%20')}",
            'imdb_id': imdb_id,
            'imdb_rating': show.get('vote_average', 'N/A')
        })
    
    return all_trending

# Function to fetch movie/show recommendations based on user input
def get_recommendations(title, genre_id=None):
    search_url = f"{TMDB_API_URL}/search/multi?api_key={TMDB_API_KEY}&query={title}"
    
    # Add filters to search if provided
    if genre_id:
        search_url += f"&with_genres={genre_id}"
    
    response = requests.get(search_url)
    results = response.json()['results']
    
    recommended_items = []
    
    for item in results[:10]:  # Limit to top 10 recommendations
        if item['media_type'] in ['movie', 'tv']:
            imdb_id = get_imdb_rating(item['id'])
            recommended_items.append({
                'title': item['title'] if item['media_type'] == 'movie' else item['name'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else None,
                'netflix_url': f"https://www.netflix.com/search?q={item['title'].replace(' ', '%20')}" if item['media_type'] == 'movie' else f"https://www.netflix.com/search?q={item['name'].replace(' ', '%20')}",
                'imdb_id': imdb_id,
                'imdb_rating': item.get('vote_average', 'N/A')
            })
    
    return recommended_items

# UI Header
st.set_page_config(page_title="Netflix Recommendation", page_icon="🎬", layout="wide")

# Centered title and subtitle with better font
st.markdown("""
    <h1 style="text-align:center; font-family: 'Comic Sans MS', cursive, sans-serif; color: #ffffff;">
        🎬 Netflix Movie & TV Show Recommendation System
    </h1>
    <h3 style="text-align:center; font-family: 'Comic Sans MS', cursive, sans-serif; color: #ffffff;">
        Discover real-time trending movies and TV shows on Netflix!
    </h3>
""", unsafe_allow_html=True)

# Center the Lottie animation
lottie_coding = load_lottiefile("netflix-logo.json")  # Path to your local Lottie file
st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
st_lottie(lottie_coding, speed=1, reverse=False, loop=True, quality="low", height=200)
st.markdown('</div>', unsafe_allow_html=True)

# Filter Section
st.subheader("🔍 Filter Recommendations")

# Genre Filter
genres = get_tmdb_genres()
genre_options = [genre['name'] for genre in genres]
selected_genre = st.selectbox("Select Genre", genre_options, index=0)

# Search Bar - Modern and Attractive
st.markdown("""<style>
    .search-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        padding: 20px;
    }
    .search-bar {
        width: 80%;
        padding: 12px;
        font-size: 16px;
        border-radius: 10px;
        border: 1px solid #ff5733;
        background-color: #f9f9f9;
        transition: 0.3s;
    }
    .search-bar:focus {
        border-color: #ff5733;
        outline: none;
        background-color: #fff;
    }
</style>""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    search_query = st.text_input("🔍 Search for a Movie or TV Show:", label_visibility="collapsed", placeholder="Enter a movie or TV show name...")
    st.markdown('</div>', unsafe_allow_html=True)

search_button = st.button("Search Recommendations", use_container_width=True)

if search_button and search_query:
    recommendations = get_recommendations(search_query, genre_id=get_genre_id(selected_genre))
    
    if recommendations:
        st.subheader(f"🔍 Recommendations for '{search_query}'")
        
        # Display recommended movies/shows with posters, IMDb ratings, and Netflix links
        for item in recommendations:
            col1, col2 = st.columns([1, 3])
            with col1:
                if item['poster_url']:
                    st.image(item['poster_url'], caption=item['title'], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/180x270?text=No+Image", use_container_width=True)
            with col2:
                st.markdown(f"### 🎥 {item['title']}")
                st.markdown(f"⭐ IMDb Rating: {item['imdb_rating']}", unsafe_allow_html=True)
                st.markdown(f"[▶ Watch on Netflix]({item['netflix_url']})", unsafe_allow_html=True)
    else:
        st.warning(f"No recommendations found for '{search_query}'")

# Real-Time Trending Movies and TV Shows
st.subheader("🔥 Real-Time Trending Movies & TV Shows on Netflix")
movies_and_shows = get_tmdb_trending(genre_id=get_genre_id(selected_genre))

if movies_and_shows:
    rows = [movies_and_shows[i:i+5] for i in range(0, len(movies_and_shows), 5)]
    
    for row in rows:
        cols = st.columns(len(row), gap="medium")
        for col, item in zip(cols, row):
            with col:
                if item['poster_url']:
                    st.image(item['poster_url'], caption=item['title'], use_container_width=True)
                    st.markdown(f"⭐ IMDb Rating: {item['imdb_rating']}", unsafe_allow_html=True)
                    st.markdown(f"[▶ Watch on Netflix]({item['netflix_url']})", unsafe_allow_html=True)
                else:
                    st.image("https://via.placeholder.com/220x300?text=No+Image", caption=item['title'], use_container_width=True)

# Footer
st.markdown('---')
st.markdown('Made with ❤️ for Netflix lovers.')
