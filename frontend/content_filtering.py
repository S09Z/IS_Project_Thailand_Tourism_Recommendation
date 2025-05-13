import os
import re
import pandas as pd
import numpy as np
import emoji
import string
import nltk
from attacut import tokenize
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from gensim.models import FastText
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

FINE_TUNED_DIR = 'pretained_or_finetune-models'
NLTK_DATA_PATH = f"{FINE_TUNED_DIR}/nltk_data"

nltk.data.path.append(NLTK_DATA_PATH)

stop_words = set(stopwords.words('english')) 
lemmatizer = WordNetLemmatizer()
# import gcsfs

# Load environment variables
load_dotenv()

# DB_HOST = os.getenv("DB_NEON_HOST")
# DB_PORT = os.getenv("DB_NEON_PORT", "5432")
# DB_NAME = os.getenv("DB_NEON_NAME")
# DB_USER = os.getenv("DB_NEON_USER")
# DB_PASSWORD = os.getenv("DB_NEON_PASSWORD")

# DB_HOST = os.getenv("DB_POSTGRES_HOST")
# DB_PORT = os.getenv("DB_POSTGRES_PORT", "5432")
# DB_NAME = os.getenv("DB_POSTGRES_DATABASE")
# DB_USER = os.getenv("DB_POSTGRES_USER")
# DB_PASSWORD = os.getenv("DB_POSTGRES_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "inputs")


def load_data_from_gcs(filename: str):
    # url = f"gs://my-streamlit-data/inputs/{filename}"
    url = f"{DATASET_DIR}/{filename}"
    return pd.read_parquet(url, engine="pyarrow")

# Example usage
tripadvisor_reviews_sentiment = load_data_from_gcs("sentiment_prediction.parquet")
tripadvisor_attractions_details = load_data_from_gcs("combined_details.parquet")
attractions_tags_cluster = load_data_from_gcs("cosine_clusters_V3.parquet")
tat_attractions = load_data_from_gcs("final_tat_attractions.parquet")
maps_tat_and_tripadvisor_ids = load_data_from_gcs("TripAdvisor_Location_Ids.parquet")
filtered_attractions_df = load_data_from_gcs("filtered_attractions_df.parquet")

if tripadvisor_reviews_sentiment.empty or attractions_tags_cluster.empty or tat_attractions.empty:
    raise ValueError("❌ One or more required tables are empty. Please check your database.")

def clean_english_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters
    text = re.sub(r'\b(u|ur|b4)\b', 'you', text)  # Replace common abbreviations
    text = text.lower()
    text = emoji.demojize(text)
    text = ''.join([char for char in text if char not in string.punctuation])
    tokens = nltk.word_tokenize(text)
    
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return ' '.join(tokens)

def clean_thai_text(text):
    """Preprocess Thai text by removing non-Thai characters and stopwords."""
    if not isinstance(text, str):
        return ""
    stopwords_list = set(thai_stopwords())
    text = re.sub(r"[^ก-๙\s]", "", text)  # Remove non-Thai characters
    tokens = word_tokenize(text)
    cleaned_tokens = [word for word in tokens if word not in stopwords_list]
    return " ".join(cleaned_tokens)

def vectorize_fasttext(text, model, vector_size=None):
    if not isinstance(text, str) or not text.strip():
        return np.zeros(model.vector_size if vector_size is None else vector_size, dtype=np.float32)

    try:
        tokens = tokenize(text)  # สมมุติว่า tokenize ดีแล้ว
    except Exception as e:
        print(f"⚠️ Tokenization error: {e}")
        return np.zeros(model.vector_size if vector_size is None else vector_size, dtype=np.float32)

    vectors = [model.wv[word] for word in tokens if word in model.wv.key_to_index]

    if not vectors:
        return np.zeros(model.vector_size if vector_size is None else vector_size, dtype=np.float32)

    return np.mean(vectors, axis=0)

EN_fasttext_model = FastText.load(f"{BASE_DIR}/EN_fasttext_model.model")
TH_fasttext_model = FastText.load(f"{BASE_DIR}/TH_fasttext_model.model")


def semantic_clustering(input_text, language="TH"):
    cleaned_input_text = ""
    TH_attraction_vectors = np.load(f"{BASE_DIR}/TH_attraction_vectors.npy")
    EN_attraction_vectors = np.load(f"{BASE_DIR}/EN_attraction_vectors.npy")
    
    if (language == "TH" and TH_attraction_vectors.size == 0) or (language == "EN" and EN_attraction_vectors.size == 0):
        print("❌ No vectors available for similarity search!")
        return []
    
    if language == "TH":
        attraction_vectors = TH_attraction_vectors
        fasttext_model = TH_fasttext_model
        cleaned_input_text = clean_thai_text(input_text)
    elif language == "EN":
        attraction_vectors = EN_attraction_vectors
        fasttext_model = EN_fasttext_model
        cleaned_input_text = clean_english_text(input_text)
    else:
        raise ValueError("❌ Unsupported language. Use 'TH' or 'EN'.")

    # ✅ Preprocess and vectorize the input text
    input_vector = vectorize_fasttext(cleaned_input_text, fasttext_model)
    input_vector = normalize(input_vector.reshape(1, -1))  # Normalize input vector

    # ✅ Compute Cosine Similarity
    similarity_scores = cosine_similarity(input_vector, attraction_vectors)[0]
    
    # for i, name in enumerate(filtered_attractions_df["place_name_th"]):
    #     if cleaned_input_text in name:
    #         similarity_scores[i] *= 1.2  # Boost water-related attractions

    # ✅ Get Top 5 Similar Attractions
    top_5_indices = np.argsort(similarity_scores)[::-1][:5]

    print("🔍 Top 5 Indices:", top_5_indices)
    print("✅ Similarity Scores:", similarity_scores[top_5_indices])

    # ✅ Map results back to `filtered_attractions_df`
    results = []
    for idx in top_5_indices:
        row = filtered_attractions_df.iloc[idx]

        place_id = row["place_id"]
        place_name = row["place_name_th"]
        merged_content = ""
        similarity_score = similarity_scores[idx]
        
        if language == "TH":
            merged_content = row["merged_attraction_content_th"]
        elif language == "EN":
            merged_content = row["merged_attraction_content_en"]
        else:
            merged_content = "N/A"

        # ✅ Retrieve location_id from `tripadvisor_reviews_sentiment`
        result_review = maps_tat_and_tripadvisor_ids[maps_tat_and_tripadvisor_ids["place_id"] == place_id]
        location_id = result_review["location_id"].tolist() if not result_review.empty else []
        
        print(f"\n\n🔍 Place ID: {place_id} / Place Name {place_name} ({similarity_score:.3f}) >>>>>>>>> [location_id: {location_id}]")

        results.append({
            "place_id": place_id,
            "location_id": location_id,
            "similarity_score": round(similarity_score, 3),
            "attraction_name": place_name,
            "most_similar_name_and_introduction": merged_content
        })

    return results