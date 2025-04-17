import sys
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# import ranking_evaluation as eval

import re
import emoji
import numpy as np
from sqlalchemy import create_engine, text
from geopy.distance import geodesic
import streamlit as st
import pandas as pd
import pydeck as pdk
from content_filtering import semantic_clustering

# Set page layout to "wide" (must be the first Streamlit command)
st.set_page_config(
    layout="wide",
    page_title="Thailand Tourism Recommendation", 
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)


# Ensure the current directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "inputs")
# DATASET_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data_from_gcs(filename: str):
    # url = f"gs://my-streamlit-data/inputs/{filename}"
    url = f"{DATASET_DIR}/{filename}"
    return pd.read_parquet(url, engine="pyarrow")

# Example usage
tripadvisor_reviews_sentiment = load_data_from_gcs("sentiment_prediction.parquet")
tripadvisor_attractions_details = load_data_from_gcs("combined_details.parquet")
attractions_tags_cluster = load_data_from_gcs("cosine_clusters.parquet")
tat_attractions = load_data_from_gcs("merged_tat_attractions.parquet")

# โหลดไฟล์เมื่อทุกไฟล์มีอยู่
# tripadvisor_reviews_sentiment = pd.read_parquet(os.path.join(DATASET_DIR, "sentiment_prediction.parquet"))
# tripadvisor_attractions_details = pd.read_parquet(os.path.join(DATASET_DIR, "combined_details.parquet"))
# attractions_tags_cluster = pd.read_parquet(os.path.join(DATASET_DIR, "cosine_clusters.parquet"))
# tat_attractions = pd.read_parquet(os.path.join(DATASET_DIR, "merged_tat_attractions.parquet"))

if "selected_places" not in st.session_state:
    st.session_state.selected_places = {}  
    st.session_state.attraction_options = []
if "segmented_control" not in st.session_state:
    st.session_state.segmented_control = None 
if "attraction_data" not in st.session_state:
    st.session_state.attraction_data = []
    
def update_selection():
    selected_label = st.session_state.segmented_control
    selected_name = st.session_state.attraction_options.get(selected_label, None)  # ✅ ดึงชื่อที่แท้จริง

    # 🔹 ถ้าผู้ใช้ "uncheck" ค่า ให้เซ็ตเป็นค่าที่เลือกไว้ล่าสุด
    if not selected_name and st.session_state.selected_places:
        st.session_state.segmented_control = next(
            (k for k, v in st.session_state.attraction_options.items() if v == st.session_state.selected_places["attraction_name"]), None
        )
        return

    # 🔹 ค้นหาข้อมูลของสถานที่ที่เลือก
    selected_obj = next((item for item in st.session_state.attraction_data if item["attraction_name"] == selected_name), None)
    if selected_obj:
        st.session_state.selected_places = selected_obj  # ✅ เก็บเป็น Object
    else:
        st.session_state.selected_places = {}

def clean_text(text):
    text = emoji.replace_emoji(text, replace='')  
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-zA-Z\u0E00-\u0E7F\s]', '', text)  
    
    if re.search(r'[a-zA-Z]', text):  # ถ้ามีตัวอักษรอังกฤษ
        text = text.lower()  # ทำ lowercase
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def filter_text_by_language(text, language):
    words = text.split()  # แยกคำออกจากกัน

    if language == "TH":
        # ✅ เก็บเฉพาะคำที่เป็นภาษาไทย
        filtered_words = [word for word in words if any("\u0E00" <= char <= "\u0E7F" for char in word)]
    elif language == "EN":
        # ✅ เก็บเฉพาะคำที่เป็นภาษาอังกฤษ
        filtered_words = [word for word in words if any("A" <= char <= "Z" or "a" <= char <= "z" for char in word)]
    else:
        filtered_words = words  # ถ้าไม่ได้เลือกภาษา ให้คืนค่าเดิม
    
    return " ".join(filtered_words) 

# def check_database_connection():
#     """Check if the database connection is successful."""
#     try:
#         with engine.connect() as connection:
#             connection.execute(text("SELECT 1"))  # Simple test query
#         return True
#     except Exception as e:
#         st.error(f"❌ Database connection failed: {e}")
#         return False
    
# def load_data_from_neon(query):
#     """Fetch data from PostgreSQL Neon into a Pandas DataFrame."""
#     with engine.connect() as connection:
#         return pd.read_sql(text(query), connection)  # ✅ Use `text(query)` for SQLAlchemy 2.x compatibility
    
def filter_locations_within_distance(cluster_df, matching_place_cluster, distance_km):
    """Filter cluster_df locations within distance_km from the center (matching_place_cluster)."""
    
    # Get center latitude and longitude
    center_lat = matching_place_cluster["latitude"].iloc[0]
    center_lon = matching_place_cluster["longitude"].iloc[0]

    # Calculate distance for each row in cluster_df
    def is_within_distance(row):
        location_coords = (row["latitude"], row["longitude"])
        center_coords = (center_lat, center_lon)
        return geodesic(center_coords, location_coords).km <= distance_km

    # Apply filtering
    filtered_df = cluster_df[cluster_df.apply(is_within_distance, axis=1)]
    
    return filtered_df


# Icon URLs (or local paths)
ICON_HOME = "https://img.icons8.com/fluency/48/home.png"  # Home icon
ICON_DATA = "https://img.icons8.com/fluency/48/table.png"  # Data icon
APP_LOGO = "https://img.icons8.com/fluency/48/sun.png"  # App logoload_dotenv()

DB_HOST = os.getenv("DB_POSTGRES_HOST")
DB_PORT = os.getenv("DB_POSTGRES_PORT", "5432")
DB_NAME = os.getenv("DB_POSTGRES_DATABASE")
DB_USER = os.getenv("DB_POSTGRES_USER")
DB_PASSWORD = os.getenv("DB_POSTGRES_PASSWORD")

# Create an SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# engine = create_engine(DATABASE_URL)

# ✅ Run the connection check before loading the app
# if check_database_connection():
#     st.success("✅ Connected to the database successfully!")
# else:
#     st.stop()

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


if menu_choice == "Data":
    st.title("Data Table")
    st.header("Tourism Authority of Thailand Attractions Dataset", divider="gray")
    st.write("-")
    # Display the DataFrame as a table
    st.dataframe(tat_attractions, use_container_width=True)


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
    st.title("ค้นหาสถานที่ท่องเที่ยว")


    trip_type_options = ["None", "Solo", "Couples", "Business", "Family", "Friends"]
    default_trip_type = st.session_state.get("trip_types", "None")
    default_index = trip_type_options.index(default_trip_type) if default_trip_type in trip_type_options else 0

    # Function to clear all form inputs
    def clear_filters():
        st.session_state["search_text"] = ""
        st.session_state["distance"] = []
        st.session_state["trip_types"] = "None"
        st.session_state["ratings"] = []

    # Initialize session state variables for the form
    if "search_text" not in st.session_state:
        st.session_state["search_text"] = ""
    if "distance" not in st.session_state:
        st.session_state["distance"] = 1000
    if "trip_types" not in st.session_state:
        st.session_state["trip_types"] = "None"
    if "ratings" not in st.session_state:
        st.session_state["ratings"] = []

    # Create the form
    with st.form("filter_form"):
        # st.header("ค้นหาสถานที่ท่องเที่ยว", divider="gray")
        
        col1, col2 = st.columns([5, 1])  # Adjust column width ratio

        # ✅ Search text input (col1)
        with col1:
            search_text = st.text_input(
                "ระบุคำค้นหา:",
                value=st.session_state["search_text"],
                key="search_text",
                placeholder="กรุณากรอกคำค้นหา...",
            )

        # ✅ Dropdown for selecting category (col2)
        with col2:
            search_language = st.radio(
                "เลือกภาษาสำหรับค้นหา: ",
                options=["TH", "EN"],
                key="search_category",
                horizontal=True,
            )
            
        filtered_search_text = filter_text_by_language(search_text, search_language)
        filtered_search_text = clean_text(filtered_search_text)

        # Search text input
        # search_text = st.text_input(
        #     "Search by keyword:",
        #     value=st.session_state["search_text"],
        #     key="search_text",
        # )
        
         # Geographic distance
        distance = st.number_input(
            "ระบุระยะทาง:",
            min_value=50,
            max_value=1000,
            value=st.session_state["distance"],
            key="distance"
        )

        # Display the selected distance
        st.write(f"(ขั้นต่ำ 50 กม., สูงสุด 1000 กม.)")

        # Trip types
        trip_types = st.selectbox(
            "ระบุประเภทการท่องเที่ยว:",
            options=trip_type_options,
            index=default_index,  #
            key="trip_types",
        )

        # Ratings
        ratings = st.multiselect(
            "ระบุคะแนน:",
            options=[1, 2, 3, 4, 5],
            default=st.session_state["ratings"],
            placeholder="เลือกคะแนน",
            key="ratings",
        )

        # Submit and Clear buttons in the same row
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("ค้นหา", type="primary", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("ล้างค่า", type="secondary", use_container_width=True, on_click=clear_filters)

    # Handle form submission
    if submit_button:
        
        st.write("### ข้อมูลค้นหา")
        st.write(f"**คำค้นหา:** {filtered_search_text}")
        st.write(f"**ระยะทาง:** {distance} กิโลเมตร")
        st.write(f"**ประเภทการเดินทาง:** {trip_types}")
        st.write(f"**คะแนนสถานที่:** {', '.join(map(str, ratings)) if ratings else 'ไม่ถูกเลือก'}")
        
        
        if filtered_search_text.strip():
            result = semantic_clustering(search_text)
            print(result)
            st.session_state.attraction_data = result  # ✅ เก็บข้อมูลเต็มไว้ใน session_state
            st.session_state.attraction_options = {
                f"{item['attraction_name']} (Score: {math.floor(item['similarity_score'] * 100000) / 100000})": item["attraction_name"]
                for item in result
            }
            st.session_state.selected_places = {} 
            st.session_state.segmented_control = None 

        else:
            st.session_state.attraction_options = []
            st.session_state.selected_places = {} 
            st.session_state.segmented_control = None 
            st.warning("ไม่พบข้อมูล กรุณาตรวจสอบคำค้นหาของท่านเป็นค่าว่าง หรือตรงตามภาษาที่เลือก หรือไม่")

if st.session_state.attraction_options:
    # if not st.session_state.segmented_control and st.session_state.attraction_options:
    #     st.session_state.segmented_control = st.session_state.attraction_options[0]
        
    st.subheader('ผลการค้นหาสถานที่ท่องเที่ยว ใกล้เคียงกับคำค้นหาของท่าน', divider="gray")
    selection = st.segmented_control(
        "เลือกสถานที่ที่ต้องการแสดง:", 
        options=list(st.session_state.attraction_options.keys()), 
        selection_mode="single",
        key="segmented_control",
        on_change=update_selection  # ✅ ใช้ฟังก์ชันอัปเดตค่า
    )

    if st.session_state.segmented_control is None or st.session_state.segmented_control == "":
        st.warning("⚠️ กรุณาเลือกสถานที่ก่อน")

    # ✅ แสดงผลค่าที่เลือก (เป็น Object)
    if isinstance(st.session_state.selected_places, dict) and st.session_state.selected_places:
        # st.write(f"🔹 คุณเลือก: {st.session_state.selected_places.get('attraction_name', 'N/A')}")
        # st.json(st.session_state.selected_places) 
        
        result = st.session_state.selected_places
        
        st.write("##### ข้อมูลสถานที่ท่องเที่ยวที่เลือก:")
        st.write(f"**TAT Place ID:** {result['place_id']}")
        st.write(f"**Similarity Score:** {result['similarity_score']}")
        st.write(f"**attraction_name:** {result['attraction_name']}")
        st.write(f"**Most Similar Name & Introduction:** {result['most_similar_name_and_introduction']}")
        
        matching_place_cluster = None
        cluster_df = None
        filtered_reviews = tripadvisor_reviews_sentiment[tripadvisor_reviews_sentiment["place_id"] == result["place_id"]]
        filtered_reviews = filtered_reviews[filtered_reviews["location_id"].isin(result['location_id'])]
        content_filtering_review = filtered_reviews.iloc[0] if not filtered_reviews.empty else None

        picked_tripadvisor_localtion_id = 0
        if len(result['location_id']) > 0:
            picked_tripadvisor_localtion_id = (result['location_id'][0])

        if content_filtering_review is not None:
            location_ids = content_filtering_review["location_id"]
            # st.dataframe(location_ids, use_container_width=True)
            if isinstance(location_ids, (int, float, np.int64)):
                location_ids = [location_ids]
                
            attractions_tags_cluster["location_id"] = attractions_tags_cluster["location_id"].fillna(0).astype(int)

            matching_place_cluster = attractions_tags_cluster[
                attractions_tags_cluster["location_id"] == int(picked_tripadvisor_localtion_id)
            ]
            
            if matching_place_cluster is not None:
                cluster_df = attractions_tags_cluster[attractions_tags_cluster["cluster"].isin(matching_place_cluster['cluster'])]
                
                print("Type of picked_tripadvisor_localtion_id:", type(picked_tripadvisor_localtion_id))
                print("Data type of location_id column:", attractions_tags_cluster["location_id"].dtype)
                print("Unique values in location_id column:", matching_place_cluster["location_id"].dtype)  # Print first 5 unique values
                print("Unique values in location_id column:", attractions_tags_cluster["location_id"].unique()[:5])  # Print first 5 unique values
                        
                print(f'==========================================result: {picked_tripadvisor_localtion_id}')
                print(matching_place_cluster['cluster'])
                print("================================================")

            if content_filtering_review is not None:
                st.write(f"**TripAdvisor สถานที่ไอดี:** {picked_tripadvisor_localtion_id}")
                if content_filtering_review is not None:
                    
                    label_mapping = {'negative': 0, 'neutral': 1, 'positive': 2}
                    tripadvisor_reviews_sentiment['sentiment'] = tripadvisor_reviews_sentiment['predicted_sentiment'].map(label_mapping)
                    
                    sentiment_sum_per_location = (
                        tripadvisor_reviews_sentiment.groupby("location_id")["sentiment"]
                        .sum()
                        .reset_index()
                        .rename(columns={"sentiment": "sentiment_calc"})
                    )
                    
                    sentiment_sum_per_location["location_id"] = sentiment_sum_per_location["location_id"].astype(str).str.replace(",", "").astype(int)
                    
                    if not matching_place_cluster.empty and matching_place_cluster is not None:
                        st.subheader(f"อยู่ใน Cluster ที่: {int(matching_place_cluster['cluster'].iloc[0])} (จำนวนแถว {len(cluster_df)}) - จัดลำดับสถานที่ท่องเที่ยวที่แนะนำ")

                        cluster_df = cluster_df.merge(sentiment_sum_per_location, on="location_id", how="left")

                        cluster_df["sentiment_calc"] = cluster_df["sentiment_calc"].fillna(0).astype(int)

                        cluster_df['total_review'] = cluster_df['rating_1_review_count'] + cluster_df['rating_2_review_count'] + cluster_df['rating_3_review_count'] + cluster_df['rating_4_review_count'] + cluster_df['rating_5_review_count']

                        sort_columns = ["sentiment_calc"]  # Always include sentiment as the first priority

                        # If the user selects ratings, use only the selected ones
                        if len(ratings) > 0:
                            for rating in sorted(ratings, reverse=True):  # Sort ratings DESC
                                sort_columns.append(f"rating_{rating}_review_count")
                        else:
                            # If no ratings are selected, sort by all review counts
                            sort_columns.extend([
                                "rating_5_review_count",
                                "rating_4_review_count",
                                "rating_3_review_count",
                                "rating_2_review_count",
                                "rating_1_review_count"
                            ])

                        if trip_types and trip_types != "None":
                            sort_columns.append(f"trip_types_{trip_types.lower()}")

                        cluster_df = cluster_df.sort_values(by=sort_columns, ascending=False)
                        
                        if distance > 0:
                            filtered_cluster_df = filter_locations_within_distance(cluster_df, matching_place_cluster, distance)
                            cluster_df = filtered_cluster_df

                        ranking_recommendation = cluster_df[['name', 'label', 'cluster', 'total_review', 'rating_5_review_count', 'rating_4_review_count', 'sentiment_calc', 'trip_types_solo', 'trip_types_couples', 'trip_types_business', 'trip_types_family', 'trip_types_friends', 'latitude', 'longitude']].head(10)

                        st.dataframe(ranking_recommendation.head(10), use_container_width=True) 

                        if len(cluster_df) > 0:
                            geoMapCoordinateData = pd.DataFrame({
                                "Province": ranking_recommendation["name"],
                                "Latitude": ranking_recommendation["latitude"],
                                "Longitude": ranking_recommendation["longitude"],
                                "Value": np.full(len(ranking_recommendation), fill_value=30)
                            })

                            icon_data = {
                                "marker": {
                                    "url": "https://upload.wikimedia.org/wikipedia/commons/e/ec/RedDot.svg",
                                    "width": 128,
                                    "height": 128,
                                    "anchorY": 128
                                }
                            }

                            layer = pdk.Layer(
                                type="IconLayer",
                                data=geoMapCoordinateData,
                                get_icon="icon_data",
                                get_position="[Longitude, Latitude]",
                                get_size=4,
                                size_scale=15,
                                pickable=True,
                            )

                            view = pdk.ViewState(
                                latitude=13.736717,
                                longitude=100.523186,
                                zoom=5,
                                pitch=0,
                            )

                            deck = pdk.Deck(
                                layers=[layer],
                                initial_view_state=view,
                                tooltip={"text": "{Province}"},
                                map_provider="carto",
                                map_style="road",
                                parameters={"iconAtlas": icon_data}
                            )

                            # Streamlit app
                            st.write("##### แผนที่แสดงสถานที่ท่องเที่ยวที่แนะนำ")
                            st.pydeck_chart(deck)
                            
                            # ✅ ให้ User ให้คะแนนผลลัพธ์แต่ละอัน
                            st.write("🎯 ให้คะแนนผลลัพธ์ที่คุณชอบ (1-10): ")
                            index = 1
                            for idx, row in ranking_recommendation.head(5).iterrows():
                                # with st.form(key=f"form_{idx}"):  # ✅ ใช้ Form ป้องกัน Refresh หน้าเว็บ
                                    # st.write(f"**🔹 [{index}] - {row['name']}**")
                                    index += 1
                                    
                            
    
                            # # ✅ แสดง Feedback ที่ได้รับ
                            # st.subheader("📊 ผลคะแนนที่ให้โดยผู้ใช้")
                            # st.json(st.session_state.user_feedback)

                    else:
                        st.write("No matching Cluster found.")
                else:
                    st.write("No matching Cluster found.")
            else:
                st.write("No matching TripAdvisor Place ID found.")