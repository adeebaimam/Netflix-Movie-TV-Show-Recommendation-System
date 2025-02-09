import pandas as pd
import requests

TMDB_API_KEY = 'cbf641a8ac1c68cbdeb959fb4fe4ea75'
TMDB_API_URL = "https://api.themoviedb.org/3"

# Fetch Genre Data (Movie and TV Show genres)
def fetch_genres():
    movie_genre_url = f"{TMDB_API_URL}/genre/movie/list?api_key={TMDB_API_KEY}"
    tv_genre_url = f"{TMDB_API_URL}/genre/tv/list?api_key={TMDB_API_KEY}"
    
    movie_response = requests.get(movie_genre_url)
    tv_response = requests.get(tv_genre_url)
    
    movie_genres = {genre['id']: genre['name'] for genre in movie_response.json()['genres']}
    tv_genres = {genre['id']: genre['name'] for genre in tv_response.json()['genres']}
    
    return movie_genres, tv_genres

# Fetch Movie Data from TMDb API
def fetch_movie_data(page=1, movie_genres=None):
    url = f"{TMDB_API_URL}/discover/movie?api_key={TMDB_API_KEY}&page={page}"
    response = requests.get(url)
    data = response.json()
    movie_data = []
    
    for movie in data['results']:
        movie_genre_names = [movie_genres.get(genre_id, 'Unknown') for genre_id in movie['genre_ids']]  # Map genre IDs to names
        
        movie_data.append({
            'show_id': movie['id'],
            'type': 'Movie',
            'title': movie['title'],
            'director': movie.get('director', 'N/A'),
            'cast': ', '.join([cast['name'] for cast in movie.get('cast', [])]),  # Example cast info
            'country': 'N/A',  # You can modify this based on TMDb data
            'date_added': 'N/A',  # You can modify this
            'release_year': movie['release_date'][:4] if movie['release_date'] else 'N/A',
            'rating': movie.get('rating', 'N/A'),
            'duration': f"{movie['runtime']} min" if 'runtime' in movie else 'N/A',
            'genres': ', '.join(movie_genre_names),  # Use the genre names
            'description': movie['overview'],
            'poster_path': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if 'poster_path' in movie else 'N/A'
        })
    
    return movie_data

# Fetch TV Show Data from TMDb API
def fetch_tv_show_data(page=1, tv_genres=None):
    url = f"{TMDB_API_URL}/discover/tv?api_key={TMDB_API_KEY}&page={page}"
    response = requests.get(url)
    data = response.json()
    tv_show_data = []

    for show in data['results']:
        tv_genre_names = [tv_genres.get(genre_id, 'Unknown') for genre_id in show['genre_ids']]  # Map genre IDs to names
        
        tv_show_data.append({
            'show_id': show['id'],
            'type': 'TV Show',
            'title': show['name'],
            'director': show.get('director', 'N/A'),
            'cast': ', '.join([cast['name'] for cast in show.get('cast', [])]),
            'country': 'N/A',  # You can modify this based on TMDb data
            'date_added': 'N/A',  # You can modify this
            'release_year': show['first_air_date'][:4] if show['first_air_date'] else 'N/A',
            'rating': show.get('rating', 'N/A'),
            'duration': 'N/A',  # TV shows usually don't have a runtime, modify if necessary
            'genres': ', '.join(tv_genre_names),  # Use the genre names
            'description': show['overview'],
            'poster_path': f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if 'poster_path' in show else 'N/A'
        })

    return tv_show_data

# Add data to CSV files
def add_data_to_csv():
    # Fetch genre data first
    movie_genres, tv_genres = fetch_genres()

    # Fetch movie and TV show data
    movie_data = fetch_movie_data(page=1, movie_genres=movie_genres)  # Modify page for more data
    tv_show_data = fetch_tv_show_data(page=1, tv_genres=tv_genres)  # Modify page for more data

    # Convert to DataFrames
    new_movies_df = pd.DataFrame(movie_data)
    new_tv_show_df = pd.DataFrame(tv_show_data)

    # Read existing data from CSV
    existing_movies_df = pd.read_csv('movies_df.csv')
    existing_tv_show_df = pd.read_csv('tv_show.csv')

    # Count how many new movies and TV shows are fetched
    new_movie_count = len(new_movies_df)
    new_tv_show_count = len(new_tv_show_df)

    # Use pd.concat to append the new data
    updated_movies_df = pd.concat([existing_movies_df, new_movies_df], ignore_index=True)
    updated_tv_show_df = pd.concat([existing_tv_show_df, new_tv_show_df], ignore_index=True)

    # Save back to CSV
    updated_movies_df.to_csv('movies_df.csv', index=False)
    updated_tv_show_df.to_csv('tv_show.csv', index=False)

    print(f"Data has been successfully updated.")
    print(f"New Movies Added: {new_movie_count}")
    print(f"New TV Shows Added: {new_tv_show_count}")

# Run the update
add_data_to_csv()
