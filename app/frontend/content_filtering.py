import os
import re
import pandas as pd
import numpy as np
from attacut import tokenize
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from gensim.models import FastText


# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_NEON_HOST")
DB_PORT = os.getenv("DB_NEON_PORT", "5432")
DB_NAME = os.getenv("DB_NEON_NAME")
DB_USER = os.getenv("DB_NEON_USER")
DB_PASSWORD = os.getenv("DB_NEON_PASSWORD")

# DB_HOST = os.getenv("DB_POSTGRES_HOST")
# DB_PORT = os.getenv("DB_POSTGRES_PORT", "5432")
# DB_NAME = os.getenv("DB_POSTGRES_DATABASE")
# DB_USER = os.getenv("DB_POSTGRES_USER")
# DB_PASSWORD = os.getenv("DB_POSTGRES_PASSWORD")

# Create an SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def load_data_from_neon(query):
    """Fetch data from PostgreSQL Neon into a Pandas DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)  # ✅ Use `text(query)` for SQLAlchemy 2.x compatibility

# ✅ Load data from PostgreSQL
tripadvisor_reviews_sentiment = load_data_from_neon("SELECT * FROM is_project.review_sentiment;")
attractions_tags_cluster = load_data_from_neon("SELECT * FROM is_project.tripadvisor_attractions_cluster;")
tat_attractions = load_data_from_neon("SELECT * FROM is_project.tat_attractions;")

# tripadvisor_reviews_sentiment = pd.read_parquet('test/prediction/SVM_TH_Prediction.parquet')
# attractions_tags_cluster = pd.read_parquet('app/clustering_experiment/output/cosine_clusters.parquet')
# tat_attractions = pd.read_csv('app/frontend/tat_attractions.csv')

if tripadvisor_reviews_sentiment.empty or attractions_tags_cluster.empty or tat_attractions.empty:
    raise ValueError("❌ One or more required tables are empty. Please check your database.")

def clean_thai_text(text):
    """Preprocess Thai text by removing non-Thai characters and stopwords."""
    if not isinstance(text, str):
        return ""
    stopwords_list = set(thai_stopwords())
    text = re.sub(r"[^ก-๙\s]", "", text)  # Remove non-Thai characters
    tokens = word_tokenize(text)
    cleaned_tokens = [word for word in tokens if word not in stopwords_list]
    return " ".join(cleaned_tokens)

def vectorize_fasttext(text, model):
    tokens = tokenize(text)  # More accurate than word_tokenize
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    
    if not vectors:
        return np.random.uniform(-0.1, 0.1, model.vector_size)
    
    return np.mean(vectors, axis=0)

# ✅ Filter data
# filtered_review_sentiment = tripadvisor_reviews_sentiment[
#     tripadvisor_reviews_sentiment["location_id"].isin(attractions_tags_cluster["location_id"])
# ]

# print(tat_attractions)


filtered_attractions_df = tat_attractions[
    tat_attractions["place_id"].isin(tripadvisor_reviews_sentiment["place_id"])
]

filtered_attractions_df.to_csv("./filtered_attractions_df.csv", index=False, encoding="utf-8")

# ✅ Ensure necessary columns exist
if "introduction_th" not in filtered_attractions_df.columns or "place_name_th" not in filtered_attractions_df.columns:
    print("❌ Missing required columns in `tat_attractions`.")

if filtered_attractions_df.empty:
    print("❌ `filtered_attractions_df` is empty. Check your database filters.")

# ✅ Preprocess and merge text
filtered_attractions_df["cleaned_introduction_th"] = filtered_attractions_df["introduction_th"].apply(lambda x: clean_thai_text(x) if isinstance(x, str) else "")
filtered_attractions_df["cleaned_place_name_th"] = filtered_attractions_df["place_name_th"].apply(lambda x: clean_thai_text(x) if isinstance(x, str) else "")

filtered_attractions_df["merged_attraction_content"] = (
    filtered_attractions_df["cleaned_introduction_th"].fillna("") + " " +
    filtered_attractions_df["cleaned_place_name_th"].fillna("")
).str.strip()


# print("🔍 Sample merged_attraction_content data:\n", filtered_attractions_df["merged_attraction_content"].head())

filtered_attractions_df = filtered_attractions_df[filtered_attractions_df["merged_attraction_content"].str.strip() != ""]

if filtered_attractions_df.empty:
    print("❌ No valid text found for training Word2Vec. Check text preprocessing.")

tokenized_sentences = [word_tokenize(text) for text in filtered_attractions_df["merged_attraction_content"] if isinstance(text, str) and text.strip()]


# print("🔍 Sample tokenized sentences:\n", tokenized_sentences[:5])

attraction_vectors = []

if not tokenized_sentences:
    print("❌ No tokenized sentences available for Word2Vec training. Ensure preprocessing is correct.")
else:
    # w2v_model = Word2Vec(vector_size=100, min_count=1, workers=4)
    # w2v_model.build_vocab(tokenized_sentences)  # ✅ Build vocabulary
    # w2v_model.train(tokenized_sentences, total_examples=w2v_model.corpus_count, epochs=w2v_model.epochs)  # ✅ Train
    fasttext_model = FastText(
        vector_size=300,
        window=10,   # Smaller window helps with short Thai words
        min_count=2,  # Ignore rare words
        workers=4,
        sg=1,  # Use Skip-Gram (better for rare words)
        min_n=2,  # Capture small subwords (better for Thai)
        max_n=6,  # More flexible subword range
        negative=10  # More negative samples = Better generalization
    )
    fasttext_model.build_vocab(tokenized_sentences)
    fasttext_model.train(tokenized_sentences, total_examples=fasttext_model.corpus_count, epochs=20)

    attraction_vectors = np.array([vectorize_fasttext(text, fasttext_model) for text in filtered_attractions_df["merged_attraction_content"]])

attraction_vectors = np.array(attraction_vectors, dtype=np.float32)

def semantic_clustering(input_text):
    if len(attraction_vectors) == 0:
        print("❌ No vectors available for similarity search!")
        return []

    # ✅ Preprocess and vectorize the input text
    cleaned_input_text = clean_thai_text(input_text)
    input_vector = vectorize_fasttext(cleaned_input_text, fasttext_model)
    input_vector = normalize(input_vector.reshape(1, -1))  # Normalize input vector

    # ✅ Compute Cosine Similarity
    similarity_scores = cosine_similarity(input_vector, attraction_vectors)[0]
    
    # ✅ Boost results containing keyword "น้ำตก"
    for i, name in enumerate(filtered_attractions_df["place_name_th"]):
        if "น้ำตก" in name:
            similarity_scores[i] *= 1.2  # Boost water-related attractions

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
        merged_content = row["merged_attraction_content"]
        similarity_score = similarity_scores[idx]

        # ✅ Retrieve location_id from `tripadvisor_reviews_sentiment`
        result_review = tripadvisor_reviews_sentiment[tripadvisor_reviews_sentiment["place_id"] == place_id]
        location_id = result_review["location_id"].tolist() if not result_review.empty else []

        results.append({
            "place_id": place_id,
            "location_id": location_id,
            "similarity_score": similarity_score,
            "Attraction Name": place_name,
            "most_similar_name_and_introduction": merged_content
        })

    return results