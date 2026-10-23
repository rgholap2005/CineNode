import streamlit as st
import pickle
import pandas as pd
import requests

# 1. Page Config
st.set_page_config(page_title="CineNode | Advanced Analytics", layout="wide", initial_sidebar_state="expanded")

if 'main_movie' not in st.session_state:
    st.session_state.main_movie = "Avatar"

# 2. Advanced CSS Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif; background-color: #0b0b0f; color: #ffffff;}
#MainMenu, footer, header, button[title="View fullscreen"] {display: none !important;}

/* Hero Section */
.hero-container {
    position: relative; border-radius: 24px; overflow: hidden; padding: 40px;
    display: flex; gap: 40px; margin-top: 20px; margin-bottom: 40px;
    background: rgba(20, 20, 25, 0.65); border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); backdrop-filter: blur(20px);
}
.hero-bg {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-size: cover; background-position: center; opacity: 0.15; filter: blur(20px); z-index: 0;
}
.hero-content {position: relative; z-index: 1; display: flex; width: 100%; gap: 40px;}
.poster-img {border-radius: 16px; width: 320px; box-shadow: 0 20px 40px rgba(0,0,0,0.8); border: 1px solid rgba(255, 255, 255, 0.1);}

/* Typography */
.movie-title {font-size: 3.5rem; font-weight: 900; margin: 0 0 5px 0; line-height: 1.1; letter-spacing: -1px;}
.movie-tagline {color: #ff528a; font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; font-style: italic;}
.movie-meta {color: #8a8a9d; font-size: 1rem; margin-bottom: 25px; display: flex; gap: 15px; align-items: center; font-weight: 600;}

/* Interactive Buttons */
.btn-group {display: flex; gap: 15px; margin-bottom: 25px;}
.btn-link {
    text-decoration: none; color: white; font-weight: 700; padding: 12px 28px;
    border-radius: 30px; display: inline-block; text-align: center;
    transition: all 0.3s ease;
}
.btn-primary {background: linear-gradient(135deg, #ff0f7b, #f89b29); box-shadow: 0 4px 15px rgba(255, 15, 123, 0.4);}
.btn-primary:hover {transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255, 15, 123, 0.6); color: white;}
.btn-secondary {background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);}
.btn-secondary:hover {background: rgba(255, 255, 255, 0.1); transform: translateY(-2px); color: white;}

/* Badges & Plot */
.tags-container {display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;}
.tag-pill {
    background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
    color: #e0e0e0; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;
}
.movie-plot {font-size: 1.1rem; line-height: 1.7; color: #b0b0c0; max-width: 800px;}

/* Advanced Analytics Cards */
.analytics-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;}
.stat-card {
    background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 20px; border-radius: 16px; text-align: left;
}
.stat-title {font-size: 0.85rem; color: #8a8a9d; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px;}
.stat-value {font-size: 1.2rem; color: #ffffff; font-weight: 600;}

/* Override Streamlit Deep Dive Button */
div.stButton > button:first-child {
    background-color: rgba(255, 255, 255, 0.05); color: white; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1); width: 100%; margin-top: 10px; font-weight: 600;
}
div.stButton > button:first-child:hover {border-color: #ff0f7b; color: #ff0f7b;}
</style>
""", unsafe_allow_html=True)


import gzip

# 3. Load Models
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(gzip.open('similarity.pkl.gz', 'rb'))

# 4. Cinematic Intelligence Mapping
cluster_aesthetics = {
    0: "Epic & Sweeping Landscapes",
    1: "High-Contrast & Gritty",
    2: "Desaturated & Meditative",
    3: "Neon-Drenched & Stylized",
    4: "Atmospheric & Moody",
    5: "Warm & Nostalgic",
    6: "Cinéma Vérité / Handheld",
    7: "Vibrant & CGI-Heavy",
    8: "Surreal & Dreamlike",
    9: "Sleek & Hyper-Polished"
}

# 5. Upgraded API Fetcher
def fetch_advanced_details(movie_id):
    api_key = "3480485df38134690d4aa070321c7e20"  # <--- PASTE API KEY HERE
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US&append_to_response=keywords"
    res = requests.get(url).json()
    
    keywords = [k['name'].title() for k in res.get('keywords', {}).get('keywords', [])][:3]
    
    return {
        "poster": f"https://image.tmdb.org/t/p/w500{res.get('poster_path', '')}" if res.get('poster_path') else "https://via.placeholder.com/500x750",
        "backdrop": f"https://image.tmdb.org/t/p/w1280{res.get('backdrop_path', '')}" if res.get('backdrop_path') else "https://via.placeholder.com/1280x720",
        "rating": round(res.get('vote_average', 0), 1),
        "runtime": res.get('runtime', 0),
        "overview": res.get('overview', 'No plot summary available.'),
        "tagline": res.get('tagline', ''),
        "genres": [g['name'] for g in res.get('genres', [])][:3],
        "tropes": keywords if keywords else ["Narrative Driven", "Character Study"]
    }

def recommend(movie):
    movie_idx = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_idx]
    # Expand to 15 recommendations
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:16] 
    
    recs = []
    for i in movies_list:
        m_id = movies.iloc[i[0]].id
        details = fetch_advanced_details(m_id)
        recs.append({"title": movies.iloc[i[0]].title, "poster": details['poster']})
    return recs

def set_movie(movie_name):
    st.session_state.main_movie = movie_name

# 6. Sidebar
st.sidebar.markdown("<h2>CineNode OS</h2>", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Navigation", ["Intelligence Engine", "Visual DNA Clusters"])

# --- PAGE 1: INTELLIGENCE ENGINE ---
if app_mode == "Intelligence Engine":
    
    current_index = int(movies[movies['title'] == st.session_state.main_movie].index[0])
    selected_movie = st.selectbox('Analyze Cinematic Data...', movies['title'].values, index=current_index)
    
    if selected_movie != st.session_state.main_movie:
        set_movie(selected_movie)
        st.rerun()

    # Fetch Data
    movie_row = movies[movies['title'] == st.session_state.main_movie].iloc[0]
    details = fetch_advanced_details(movie_row.id)
    
    # Calculate Custom Metrics
    vibe = cluster_aesthetics.get(movie_row.get('cluster', 0), "Standard Dynamic Range")
    pacing = "Slow-Burn / Methodical" if details['runtime'] > 130 else "Kinetic / Fast-Paced"
    
    tags_html = "".join([f'<div class="tag-pill">{genre}</div>' for genre in details['genres']])
    tropes_str = " • ".join(details['tropes'])
    tagline_html = f"<p class='movie-tagline'>\"{details['tagline']}\"</p>" if details['tagline'] else ""
    
    # Render Hero Interface
    # Render Hero Interface
    st.markdown(f"""
<div class="hero-container">
    <div class="hero-bg" style="background-image: url('{details['backdrop']}');"></div>
    <div class="hero-content">
        <img src="{details['poster']}" class="poster-img">
        <div style="flex-grow: 1;">
            <h1 class="movie-title">{st.session_state.main_movie}</h1>
            {tagline_html}
            <div class="movie-meta">
                <span>{details['rating']} / 10</span> <span>•</span> <span>{details['runtime']} mins</span>
            </div>
            <div class="btn-group">
                <a href="https://www.themoviedb.org/movie/{movie_row.id}" target="_blank" class="btn-link btn-primary">Watch Trailer</a>
                <a href="https://letterboxd.com/search/{st.session_state.main_movie.replace(' ', '+')}/" target="_blank" class="btn-link btn-secondary">Community Reviews</a>
            </div>
            <div class="tags-container">{tags_html}</div>
            <p class="movie-plot">{details['overview']}</p>
            <div class="analytics-grid">
                <div class="stat-card">
                    <div class="stat-title">Visual Profile</div>
                    <div class="stat-value">{vibe}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Rhythm & Pacing</div>
                    <div class="stat-value">{pacing}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Core Tropes</div>
                    <div class="stat-value">{tropes_str}</div>
                </div>
            </div>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)

# --- PAGE 2: CLUSTERS ---
elif app_mode == "Visual DNA Clusters":
    st.markdown("<h1>Visual DNA Mapping 🌌</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a0a0b0;'>AI-driven grouping based on cinematography, color theory, and narrative structure.</p>", unsafe_allow_html=True)
    
    selected_cluster = st.selectbox("Select a Cinematic Profile:", range(10), format_func=lambda x: f"Cluster {x}: {cluster_aesthetics.get(x, '')}")
    
    if st.button("Extract Film Data"):
        cluster_movies = movies[movies['cluster'] == selected_cluster].head(10)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='margin-bottom: 20px;'>Matches your Aesthetic Criteria</h3>", unsafe_allow_html=True)
    recs = recommend(st.session_state.main_movie)
    
    # Renders 15 movies across 3 dynamic rows
    for i in range(0, 15, 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(recs):
                with cols[j]:
                    st.image(recs[i+j]['poster'], use_column_width=True)
                    if st.button(f"Analyze {recs[i+j]['title']}", key=f"btn_{i+j}"):
                        set_movie(recs[i+j]['title'])
                        st.rerun()
        st.write("") # Adds clean vertical spacing between rows
        for idx in range(10):
            if idx < len(cluster_movies):
                col = cols[idx % 5]
                m_id = cluster_movies.iloc[idx]['id']
                details = fetch_advanced_details(m_id)
                with col:
                    st.image(details['poster'], use_column_width=True)
                    st.markdown(f"<p style='text-align:center; font-size:0.9rem; font-weight:600; margin-top:10px;'>{cluster_movies.iloc[idx]['title']}</p>", unsafe_allow_html=True)
            if idx == 4:
                st.write("")