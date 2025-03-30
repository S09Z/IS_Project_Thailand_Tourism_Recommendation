import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(layout="wide")
# Load data
st.title("Data Table")
st.write("This is the Data page where you can display data in table format.")

# Load the dataset
merged_tat_attractions_df = pd.read_csv('./merged_tat_attractions.csv')

# Display the DataFrame as a table
st.dataframe(merged_tat_attractions_df, use_container_width=True)

# Text input for user query
user_input = st.text_input("Enter your input below (keyword or phrase):")

# Search and display results when user inputs a value
if user_input:
    # Check if "introduction_th" column has valid non-empty values
    if "introduction_th" in merged_tat_attractions_df.columns:
        # Fill NaN values in "introduction_th" for vectorization
        merged_tat_attractions_df["introduction_th"].fillna("", inplace=True)
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(merged_tat_attractions_df["introduction_th"])

        # Transform user input into TF-IDF vector
        user_query_vector = vectorizer.transform([user_input])

        # Compute cosine similarity
        similarity_scores = cosine_similarity(user_query_vector, tfidf_matrix).flatten()

        # Add similarity scores to the DataFrame
        merged_tat_attractions_df["cosine_similarity"] = similarity_scores

        # Sort results by similarity
        top_results = merged_tat_attractions_df.sort_values(by="cosine_similarity", ascending=False).head(5)

        # Display top results
        st.write("### Top Matching Results")
        st.dataframe(top_results[["placeId", "place_name_th", "introduction_th", "cosine_similarity"]])

    else:
        st.error("The column 'introduction_th' does not exist in the dataset.")
