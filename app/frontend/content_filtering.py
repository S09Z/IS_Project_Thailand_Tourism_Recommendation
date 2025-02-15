import pandas as pd
import numpy as np
from pythainlp import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
import re

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

# Load attraction data once (avoiding multiple reads)
tripadvisor_reviews_sentiment = pd.read_csv('./../../test/prediction/SVN_Prediction.csv', encoding='utf-8').reset_index(drop=True)
attractions_tags_cluster = pd.read_csv("./clustering_experiment/input/tag_embeddings.csv")
tat_attractions = pd.read_csv("../frontend/merged_tat_attractions.csv")

print("tat_attractions sample:\n", tat_attractions.head())
print("tripadvisor_reviews_sentiment sample:\n", tripadvisor_reviews_sentiment.head())


# tat_attractions = tat_attractions.dropna(subset=["placeId"])
# tripadvisor_reviews_sentiment = tripadvisor_reviews_sentiment.dropna(subset=["place_id"])

# tat_attractions.rename(columns=lambda x: x.strip().lower(), inplace=True)
# tripadvisor_reviews_sentiment.rename(columns=lambda x: x.strip().lower(), inplace=True)
filterd_review_sentiment = tripadvisor_reviews_sentiment[tripadvisor_reviews_sentiment["location_id"].isin(attractions_tags_cluster["location_id"])]

filtered_attractions_df = tat_attractions[tat_attractions["placeId"].isin(filterd_review_sentiment["place_id"])]

filtered_attractions_df["cleaned_introduction_th"] = filtered_attractions_df["introduction_th"].apply(lambda x: clean_thai_text(x))
filtered_attractions_df["cleaned_place_name_th"] = filtered_attractions_df["place_name_th"].apply(lambda x: clean_thai_text(x))


filtered_attractions_df["merged_attraction_content"] = (
    filtered_attractions_df["cleaned_introduction_th"].fillna("") + " " +
    filtered_attractions_df["cleaned_place_name_th"].fillna("")
).str.strip()

w2v_model = Word2Vec(sentences=[word_tokenize(text) for text in filtered_attractions_df["merged_attraction_content"]],
                     vector_size=100, min_count=1)

# # Precompute vectors for all attractions
attraction_vectors = np.array([vectorize_word2vec(text, w2v_model) for text in filtered_attractions_df["merged_attraction_content"]])

def semantic_clustering(input_text):
    """Find the most semantically similar attraction for the given input text."""
    cleaned_input_text = clean_thai_text(input_text)
    input_vector = vectorize_word2vec(cleaned_input_text, w2v_model)

    # # Compute similarity
    similarity_scores = cosine_similarity([input_vector], attraction_vectors)[0]
    most_similar_index = np.argmax(similarity_scores)

    result_review = tripadvisor_reviews_sentiment[tripadvisor_reviews_sentiment["place_id"] == filtered_attractions_df.iloc[most_similar_index]["placeId"]]
    
    print("result_review:\n", result_review["location_id"])

    # # Return the best match
    return {
        "place_id": filtered_attractions_df.iloc[most_similar_index]["placeId"],
        "location_id": result_review["location_id"],
        "similarity_Score": similarity_scores[most_similar_index],
        "Attraction Name": filtered_attractions_df.iloc[most_similar_index]["place_name_th"],
        "most_similar_name_and_introduction": filtered_attractions_df.iloc[most_similar_index]["merged_attraction_content"]
    }
