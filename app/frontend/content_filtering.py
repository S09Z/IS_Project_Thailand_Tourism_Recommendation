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
attractions_df = pd.read_csv("../frontend/merged_tat_attractions.csv").dropna(subset=["introduction_th"])
attractions_df["cleaned_introduction_th"] = attractions_df["introduction_th"].apply(lambda x: clean_thai_text(x))

w2v_model = Word2Vec(sentences=[word_tokenize(text) for text in attractions_df["cleaned_introduction_th"]],
                     vector_size=100, min_count=1)

# Precompute vectors for all attractions
attraction_vectors = np.array([vectorize_word2vec(text, w2v_model) for text in attractions_df["cleaned_introduction_th"]])


def semantic_clustering(input_text):
    """Find the most semantically similar attraction for the given input text."""
    cleaned_input_text = clean_thai_text(input_text)
    input_vector = vectorize_word2vec(cleaned_input_text, w2v_model)
    
    # Compute similarity
    similarity_scores = cosine_similarity([input_vector], attraction_vectors)[0]
    most_similar_index = np.argmax(similarity_scores)
    
    # Return the best match
    return {
        "place_id": attractions_df.iloc[most_similar_index]["placeId"],
        "Attraction Name": attractions_df.iloc[most_similar_index]["place_name_th"],
        "Most Similar Review": attractions_df.iloc[most_similar_index]["introduction_th"]
    }
