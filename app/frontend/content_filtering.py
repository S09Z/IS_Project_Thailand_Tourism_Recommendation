import os
import re
import pandas as pd
import numpy as np
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_NEON_HOST")
DB_PORT = os.getenv("DB_NEON_PORT", "5432")
DB_NAME = os.getenv("DB_NEON_NAME")
DB_USER = os.getenv("DB_NEON_USER")
DB_PASSWORD = os.getenv("DB_NEON_PASSWORD")

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

# ✅ Ensure data is not empty before processing
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

def vectorize_word2vec(text, model):
    """Convert text into a vector representation using Word2Vec."""
    tokens = word_tokenize(text)
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

print("\n📦 📦 📦  >>>>>>>>>>>>>>> tat_attractions.\n")
print(tat_attractions.head(5))

print("\n📦 📦 📦  >>>>>>>>>>>>>>> attractions_tags_cluster\n")
print(attractions_tags_cluster.head(5))

print("\n📦 📦 📦  >>>>>>>>>>>>>>> tripadvisor_reviews_sentiment\n")
print(tripadvisor_reviews_sentiment.head(5))

# ✅ Filter data
filtered_review_sentiment = tripadvisor_reviews_sentiment[
    tripadvisor_reviews_sentiment["location_id"].isin(attractions_tags_cluster["location_id"])
]

filtered_attractions_df = tat_attractions[
    tat_attractions["place_id"].isin(filtered_review_sentiment["place_id"])
]

print("\n📦 📦 📦  >>>>>>>>>>>>>>> filtered_review_sentiment\n")
print(filtered_review_sentiment.head(5))

print("\n📦 📦 📦  >>>>>>>>>>>>>>> filtered_attractions_df\n")
print(filtered_attractions_df.head(5))

# ✅ Ensure necessary columns exist
if "introduction_th" not in filtered_attractions_df.columns or "place_name_th" not in filtered_attractions_df.columns:
    raise KeyError("❌ Missing required columns in `tat_attractions`.")
# ✅ Ensure `filtered_attractions_df` is not empty
if filtered_attractions_df.empty:
    raise ValueError("❌ `filtered_attractions_df` is empty. Check your database filters.")

# ✅ Preprocess and merge text
filtered_attractions_df["cleaned_introduction_th"] = filtered_attractions_df["introduction_th"].apply(lambda x: clean_thai_text(x) if isinstance(x, str) else "")
filtered_attractions_df["cleaned_place_name_th"] = filtered_attractions_df["place_name_th"].apply(lambda x: clean_thai_text(x) if isinstance(x, str) else "")

filtered_attractions_df["merged_attraction_content"] = (
    filtered_attractions_df["cleaned_introduction_th"].fillna("") + " " +
    filtered_attractions_df["cleaned_place_name_th"].fillna("")
).str.strip()

# ✅ Debug: Print first 5 rows of merged text
print("🔍 Sample merged_attraction_content data:\n", filtered_attractions_df["merged_attraction_content"].head())

# ✅ Filter out empty rows
filtered_attractions_df = filtered_attractions_df[filtered_attractions_df["merged_attraction_content"].str.strip() != ""]

# ✅ Ensure text exists before training
if filtered_attractions_df.empty:
    raise ValueError("❌ No valid text found for training Word2Vec. Check text preprocessing.")

# ✅ Prepare tokenized sentences
tokenized_sentences = [word_tokenize(text) for text in filtered_attractions_df["merged_attraction_content"] if isinstance(text, str) and text.strip()]

# ✅ Debug: Print tokenized sentences sample
print("🔍 Sample tokenized sentences:\n", tokenized_sentences[:5])

# ✅ Ensure tokenized sentences are valid
if not tokenized_sentences:
    raise ValueError("❌ No tokenized sentences available for Word2Vec training. Ensure preprocessing is correct.")

# ✅ Initialize and train Word2Vec model
w2v_model = Word2Vec(vector_size=100, min_count=1, workers=4)
w2v_model.build_vocab(tokenized_sentences)  # ✅ Build vocabulary
w2v_model.train(tokenized_sentences, total_examples=w2v_model.corpus_count, epochs=w2v_model.epochs)  # ✅ Train


# ✅ Precompute vectors for all attractions
attraction_vectors = np.array([vectorize_word2vec(text, w2v_model) for text in filtered_attractions_df["merged_attraction_content"]])

def semantic_clustering(input_text):
    """Find the most semantically similar attraction for the given input text."""
    cleaned_input_text = clean_thai_text(input_text)
    input_vector = vectorize_word2vec(cleaned_input_text, w2v_model)

    # ✅ Compute similarity
    similarity_scores = cosine_similarity([input_vector], attraction_vectors)[0]
    most_similar_index = np.argmax(similarity_scores)

    # ✅ Handle potential key mismatch
    if "place_id" not in filtered_attractions_df.columns:
        raise KeyError("❌ Column `place_id` is missing in `filtered_attractions_df`.")

    # ✅ Get the result review
    place_id = filtered_attractions_df.iloc[most_similar_index]["place_id"]
    result_review = tripadvisor_reviews_sentiment[tripadvisor_reviews_sentiment["place_id"] == place_id]

    if result_review.empty:
        raise ValueError(f"❌ No reviews found for place_id: {place_id}")

    # ✅ Ensure `location_id` column exists
    if "location_id" not in result_review.columns:
        raise KeyError("❌ Column `location_id` is missing in `tripadvisor_reviews_sentiment`.")

    print("Result review:\n", result_review["location_id"])

    # ✅ Return the best match
    return {
        "place_id": place_id,
        "location_id": result_review["location_id"].tolist(),
        "similarity_Score": similarity_scores[most_similar_index],
        "Attraction Name": filtered_attractions_df.iloc[most_similar_index]["place_name_th"],
        "most_similar_name_and_introduction": filtered_attractions_df.iloc[most_similar_index]["merged_attraction_content"]
    }
