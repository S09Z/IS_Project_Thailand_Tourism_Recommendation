
import pandas as pd
import numpy as np
from pythainlp import word_tokenize
from sklearn.metrics.pairwise import pairwise_kernels


from pythainlp.corpus.common import thai_stopwords
from pythainlp.tokenize import word_tokenize
import re

from gensim.models import Word2Vec

from pythainlp import word_vector

def clean_thai_text(text):
    if not isinstance(text, str):
        return ""
    stopwords_list = set(thai_stopwords())
    # Remove non-Thai characters and numbers
    text = re.sub(r"[^ก-๙\s]", "", text)
    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    cleaned_tokens = [word for word in tokens if word not in stopwords_list]
    return " ".join(cleaned_tokens)

def pairwise_custom_kernel(x, y, metric='cosine'):
    return pairwise_kernels(x, y, metric=metric)


def vectorize_word2vec(text, model):
    tokens = word_tokenize(text)
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)


thai2vec_model = word_vector.WordVector(model_name="thai2fit_wv").get_model()

attractions_df = pd.read_csv("./frontend/merged_tat_attractions.csv")

attractions_df = attractions_df.dropna(subset=["introduction_th"])
attractions_df["cleaned_introduction_th"] = attractions_df["introduction_th"].apply(clean_thai_text)
input_text = "เล่นน้ำ"
cleaned_input_text = clean_thai_text(input_text)

# Train Word2Vec model
w2v_model = Word2Vec(sentences=[word_tokenize(text) for text in attractions_df["cleaned_introduction_th"]],
                     vector_size=100, min_count=1)

w2v_review_vectors = np.array([vectorize_word2vec(text, w2v_model) for text in attractions_df["cleaned_introduction_th"]])
w2v_input_vector = vectorize_word2vec(cleaned_input_text, w2v_model)
    

w2v_pairwise_similarity_scores = pairwise_custom_kernel([w2v_input_vector], w2v_review_vectors, metric='cosine')
w2v_pairwise_most_similar_index = np.argmax(w2v_pairwise_similarity_scores)

print("\nPairwise Kernel")
print("Attraction Name:", attractions_df.iloc[w2v_pairwise_most_similar_index]["place_name_th"])
print("Most Similar Review:", attractions_df.iloc[w2v_pairwise_most_similar_index]["introduction_th"])
print("Similarity Score:", w2v_pairwise_similarity_scores[0, w2v_pairwise_most_similar_index])