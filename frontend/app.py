import streamlit as st
import pickle
import os
import gdown
import requests

# --- Constants ---
MODEL_DIR = 'models'
MODEL_FILES = {
    'movie_list.pkl': '1f0TRr7xTGYBhQnLLXGnr1k-MwsCWDDrj',
    'similarity.pkl': '1pBXtzWAwzlT0usDx39XK2LneLw88voGL'
}
TMDB_API_KEY = 'fa52ad6723e7d41ea4b2cf57a87d48eb'  # <--- Replace with your actual TMDB API key

# --- Ensure models/ exists ---
os.makedirs(MODEL_DIR, exist_ok=True)

# --- Download missing model files from Google Drive ---
for filename, file_id in MODEL_FILES.items():
    file_path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(file_path):
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, file_path, quiet=False)

# --- Load Models ---
movie_list_path = os.path.join(MODEL_DIR, 'movie_list.pkl')
similarity_path = os.path.join(MODEL_DIR, 'similarity.pkl')

movies = pickle.load(open(movie_list_path, 'rb'))
similarity = pickle.load(open(similarity_path, 'rb'))

# --- Helper to get IMDb link from TMDB ---
def get_imdb_link(movie_title):
    search_url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_title
    }
    response = requests.get(search_url, params=params)
    data = response.json()

    if data['results']:
        movie_id = data['results'][0]['id']
        external_ids_url = f'https://api.themoviedb.org/3/movie/{movie_id}/external_ids'
        external_response = requests.get(external_ids_url, params={'api_key': TMDB_API_KEY})
        external_data = external_response.json()
        imdb_id = external_data.get('imdb_id')
        if imdb_id:
            return f'https://www.imdb.com/title/{imdb_id}/'
    return None

# --- Recommend Function ---
def recommend(movie):
    index = movies[movies['Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].Title
        recommended_movie_names.append(title)
    return recommended_movie_names

# --- Styling ---
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Rubik:wght@500;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Rubik', sans-serif;
        color: white;
    }

    .stApp {
        background-image: url("https://c1.wallpaperflare.com/preview/570/413/91/interior-theatre-theater-empty-theater.jpg");
        background-size: cover;
    }

    .movie-card {
        margin-bottom: 16px;
        padding: 16px 20px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.07);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.15);
    }

    .movie-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: scale(1.015);
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.4);
        cursor: pointer;
    }

    .movie-title {
        font-size: 20px;
        font-weight: 600;
        color: white;
        margin-bottom: 6px;
    }

    .imdb-link {
        text-decoration: none;
        color: #ffcc00;
        font-weight: 600;
        font-size: 16px;
    }

    .imdb-link:hover {
        color: #ffa500;
    }

    .main-title {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        margin-top: 20px;
        color: #ffcc00;
    }

    .subtitle {
        font-size: 20px;
        font-weight: 500;
        text-align: center;
        color: #ffffffcc;
        margin-bottom: 30px;
    }

    .dropdown-label {
        font-size: 18px !important;
        font-weight: 600;
        margin-bottom: 12px;
    }
    </style>
''', unsafe_allow_html=True)

# --- UI ---
st.markdown("""
    <div class='main-title'>🍿 Movie Recommendation System</div>
    <div class='subtitle'>Find similar movies instantly!</div>
""", unsafe_allow_html=True)

movie_list = movies['Title'].values
st.markdown("<div class='dropdown-label'>🎥 Select a movie to get recommendations:</div>", unsafe_allow_html=True)
selected_movie = st.selectbox("", movie_list)

if st.button('🔍 Show Recommendations'):
    recommended_movie_names = recommend(selected_movie)
    st.markdown("## ✅ Recommendations:")
    for name in recommended_movie_names:
        imdb_url = get_imdb_link(name)
        if imdb_url:
            st.markdown(
                f"""
                <div class='movie-card'>
                    <div class='movie-title'>🎬 {name}</div>
                    <a href='{imdb_url}' target='_blank' class='imdb-link'>🔗 View on IMDb</a>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"- **{name}** 👉 IMDb link not found", unsafe_allow_html=True)