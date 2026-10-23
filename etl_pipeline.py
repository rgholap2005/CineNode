import requests
import pandas as pd
import pickle
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

# 1. Pipeline Configuration
API_KEY = "3480485df38134690d4aa070321c7e20"
PAGES_TO_FETCH = 5 # Fetches the top 100 most popular recent movies (20 pages = 400 movies)
START_YEAR = "2017-01-01"
END_YEAR = "2026-12-31"

print("Initiating ETL Pipeline: Extracting modern film data from TMDB...")

new_movies = []

# 2. Data Extraction (Scraping TMDB)
for page in range(1, PAGES_TO_FETCH + 1):
    discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&primary_release_date.gte={START_YEAR}&primary_release_date.lte={END_YEAR}&page={page}"
    response = requests.get(discover_url).json()
    
    for movie in response.get('results', []):
        movie_id = movie['id']
        title = movie['title']
        
        # Hit the specific movie endpoint to get cast, crew, and keywords
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits,keywords"
        try:
            details = requests.get(details_url).json()
            
            # Feature Extraction (Formatting to match your ML logic)
            genres = [g['name'].replace(" ", "") for g in details.get('genres', [])]
            keywords = [k['name'].replace(" ", "") for k in details.get('keywords', {}).get('keywords', [])]
            
            # Get top 3 cast members
            cast = [c['name'].replace(" ", "") for c in details.get('credits', {}).get('cast', [])][:3]
            
            # Get Director
            crew = details.get('credits', {}).get('crew', [])
            director = [c['name'].replace(" ", "") for c in crew if c['job'] == 'Director']
            
            # Engineer the 'tags' column for the Vectorizer
            tags = " ".join(genres + keywords + cast + director + details.get('overview', '').split())
            
            new_movies.append({'id': movie_id, 'title': title, 'tags': tags.lower()})
        except Exception as e:
            continue
        
        time.sleep(0.1) # Prevent hitting API rate limits

# 3. Data Transformation (Merging with old data)
print(f"Extraction complete. {len(new_movies)} new movies staged. Transforming vectors...")

# Load existing database
old_dict = pickle.load(open('movie_dict.pkl', 'rb'))
old_df = pd.DataFrame(old_dict)

# Create a DataFrame for new movies and merge them
new_df = pd.DataFrame(new_movies)

# Prevent duplicates if the pipeline is run multiple times
combined_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['id'], keep='last').reset_index(drop=True)

# 4. Machine Learning Model Retraining
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(combined_df['tags']).toarray()

# Rebuild Cosine Similarity Matrix
similarity = cosine_similarity(vectors)

# Rebuild K-Means Cinematic Clusters
kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
combined_df['cluster'] = kmeans.fit_predict(vectors)

# 5. Data Loading (Hot-Swapping the .pkl files)
pickle.dump(combined_df.to_dict(), open('movie_dict.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print(f"Pipeline Complete! Database upgraded to {len(combined_df)} films. Machine Learning models successfully overwritten.")