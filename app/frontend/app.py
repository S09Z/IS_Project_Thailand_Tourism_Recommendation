import sys
import os

# Ensure the current directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import pydeck as pdk
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from content_filtering import semantic_clustering

# Set page layout to "wide" (must be the first Streamlit command)
st.set_page_config(layout="wide")

# Icon URLs (or local paths)
ICON_HOME = "https://img.icons8.com/fluency/48/home.png"  # Home icon
ICON_DATA = "https://img.icons8.com/fluency/48/table.png"  # Data icon
APP_LOGO = "https://img.icons8.com/fluency/48/sun.png"  # App logo

# Custom Logo and Title in Sidebar
st.sidebar.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0;">
        <img src="{APP_LOGO}" width="30" height="30">
        <h2 style="margin: 0; font-size: 1.25rem;">Murpheys09z</h2>
    </div>
    <hr style="margin-top: 10px; margin-bottom: 10px;">
    """,
    unsafe_allow_html=True,
)

# Sidebar Menu with Functional Buttons
menu_choice = "Home"  # Default page
if st.sidebar.button(f"🏠   Home", use_container_width=False, type="tertiary"):
    menu_choice = "Home"
if st.sidebar.button(f"📊   Data", use_container_width=False, type="tertiary"):
    menu_choice = "Data"

merged_tat_attractions_df = pd.read_csv('./merged_tat_attractions.csv')
tripadvisor_attractions_details = pd.read_csv('./data/combined_details.csv')
tripadvisor_reviews_sentiment = pd.read_csv('./../../test/prediction/SVN_Prediction.csv', encoding='utf-8').reset_index(drop=True)
attractions_tags_cluster = pd.read_csv("./clustering_experiment/input/tag_embeddings.csv")

if menu_choice == "Data":
    st.title("Data Table")
    st.header("Tourism Authority of Thailand Attractions Dataset", divider="gray")
    st.write("-")
    # Display the DataFrame as a table
    st.dataframe(merged_tat_attractions_df, use_container_width=True)


    st.header("Tripadvisor Attractions Details Dataset", divider="gray")
    st.write("-")

    # Display the DataFrame as a table
    st.dataframe(tripadvisor_attractions_details, use_container_width=True)


    st.header("Tripadvisor Reviews Sentiment Analysis Dataset", divider="gray")
    st.write("-")

    # Display the DataFrame as a table
    st.dataframe(tripadvisor_reviews_sentiment, use_container_width=True)
    
    st.header("Attractions Tags Clustering Dataset", divider="gray")
    st.write("-")

    # Display the DataFrame as a table
    st.dataframe(attractions_tags_cluster, use_container_width=True)
        

    # Download option
    # csv = merged_tat_attractions_df.to_csv(index=False).encode("utf-8")
    # st.download_button(
    #     label="Download data as CSV",
    #     data=csv,
    #     file_name="data.csv",
    #     mime="text/csv",
    # )

# Main Page Content Based on Menu Selection
elif menu_choice == "Home":
    # App title
    st.title("Filter TripAdvisor Reviews")

    geoMapCoordinateData = pd.DataFrame({
        "Province": ["Bangkok", "Chiang Mai", "Phuket", "Khon Kaen", "Chon Buri"],
        "Latitude": [13.736717, 18.788344, 7.880448, 16.441934, 13.361143],
        "Longitude": [100.523186, 98.985300, 98.398102, 102.835223, 100.984671],
        "Value": [100, 50, 70, 30, 60],  # Example values
    })

    # Function to clear all form inputs
    def clear_filters():
        st.session_state["search_text"] = ""
        st.session_state["regions"] = []
        st.session_state["trip_types"] = []
        st.session_state["ratings"] = []

    # Initialize session state variables for the form
    if "search_text" not in st.session_state:
        st.session_state["search_text"] = ""
    if "regions" not in st.session_state:
        st.session_state["regions"] = []
    if "trip_types" not in st.session_state:
        st.session_state["trip_types"] = []
    if "ratings" not in st.session_state:
        st.session_state["ratings"] = []

    # Create the form
    with st.form("filter_form"):
        st.header("Filter Reviews")

        # Search text input
        search_text = st.text_input(
            "Search by keyword:",
            value=st.session_state["search_text"],
            key="search_text",
        )

        # Geographic regions
        regions = st.multiselect(
            "Select regions:",
            options=["Central", "Northern", "Southern", "Eastern", "Western", "Northeastern"],
            default=st.session_state["regions"],
            key="regions",
        )

        # Trip types
        trip_types = st.multiselect(
            "Select trip types:",
            options=["Couple", "Family", "Alone", "Friends", "Business"],
            default=st.session_state["trip_types"],
            key="trip_types",
        )

        # Ratings
        ratings = st.multiselect(
            "Select ratings:",
            options=[1, 2, 3, 4, 5],
            default=st.session_state["ratings"],
            key="ratings",
        )

        # Submit and Clear buttons in the same row
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("Apply Filters", type="primary", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Clear Filters", type="secondary", use_container_width=True, on_click=clear_filters)

    # Pydeck Layer
    # layer = pdk.Layer(
    #     "ScatterplotLayer",
    #     data=geoMapCoordinateData,
    #     get_position="[Longitude, Latitude]",
    #     get_radius="Value * 1000",  # Adjust size based on Value
    #     get_fill_color="[Value * 2, 100, 150, 128]",  # Set 128 for 50% transparency (RGBA)
    #     pickable=True,
    # )

    # Pydeck View
    # view = pdk.ViewState(
    #     latitude=13.736717,
    #     longitude=100.523186,
    #     zoom=5,
    #     pitch=50,
    # )

    # Pydeck Deck
    # r = pdk.Deck(
    #     layers=[layer],
    #     initial_view_state=view,
    #     tooltip={"text": "{Province}\nValue: {Value}"},
    # )

    # Streamlit app
    # st.title("Thailand Geo Map by Province")
    # st.pydeck_chart(r)

    # Handle form submission
    if submit_button:
        st.write("### Applied Filters")
        st.write(f"**Keyword:** {search_text}")
        st.write(f"**Regions:** {', '.join(regions) if regions else 'None selected'}")
        st.write(f"**Trip Types:** {', '.join(trip_types) if trip_types else 'None selected'}")
        st.write(f"**Ratings:** {', '.join(map(str, ratings)) if ratings else 'None selected'}")

        if search_text.strip():
            # Call the function and get results
            result = semantic_clustering(search_text)

            # Display results
            st.subheader("Best Matched Attraction:")
            st.write(f"**place_id:** {result['place_id']}")
            st.write(f"**Attraction Name:** {result['Attraction Name']}")
            st.write(f"**Most Similar Review:** {result['Most Similar Review']}")
        else:
            st.warning("Please enter some text to search.")