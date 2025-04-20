import streamlit as st
import pickle
import os
import gdown

# --- Constants ---
MODEL_DIR = 'models'
MODEL_FILES = {
    'movie_list.pkl': '1f0TRr7xTGYBhQnLLXGnr1k-MwsCWDDrj',
    'similarity.pkl': '1pBXtzWAwzlT0usDx39XK2LneLw88voGL'
}

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

# --- Recommend Function ---
def recommend(movie):
    index = movies[movies['Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    for i in distances[1:6]:
        recommended_movie_names.append(movies.iloc[i[0]].Title)
    return recommended_movie_names

# --- Background Image (URL-based) ---
page_bg_img = '''
<style>
.stApp {
  background-image: url("https://c1.wallpaperflare.com/preview/570/413/91/interior-theatre-theater-empty-theater.jpg");
  background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Streamlit UI ---
st.markdown('# 🎬 Movie Recommendation System')

movie_list = movies['Title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names = recommend(selected_movie)
    for name in recommended_movie_names:
        st.subheader(name)
