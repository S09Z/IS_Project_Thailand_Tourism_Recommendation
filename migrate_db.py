import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from tqdm import tqdm 

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Retrieve database credentials from .env
DB_HOST = os.getenv("DB_NEON_HOST")
DB_PORT = os.getenv("DB_NEON_PORT")
DB_NAME = os.getenv("DB_NEON_NAME")
DB_USER = os.getenv("DB_NEON_USER")
DB_PASSWORD = os.getenv("DB_NEON_PASSWORD")


def connect_db():
    """Establish a connection to NeonDB PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )


def create_schema():
    """Ensure the 'is_project' schema exists."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS is_project;")
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Schema 'is_project' ensured.")


def create_review_sentiment_table():
    """Create 'review_sentiment' table inside 'is_project' schema."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS is_project.review_sentiment (
            id SERIAL PRIMARY KEY,
            place_id TEXT,
            location_id TEXT,
            review_text TEXT,
            actual_sentiment TEXT,
            predicted_sentiment TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'review_sentiment' ensured.")


def import_review_sentiment(csv_file):
    """Import data from CSV into 'review_sentiment'."""
    conn = connect_db()
    cursor = conn.cursor()
    
    df = pd.read_csv(csv_file)

    print(f"📥 Importing {len(df)} rows into 'is_project.review_sentiment'...")
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Progress", unit="row"):
        cursor.execute(
            """
            INSERT INTO is_project.review_sentiment (place_id, location_id, review_text, actual_sentiment, predicted_sentiment)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (row["place_id"], row["location_id"], row["review_text"], row["actual_sentiment"], row["predicted_sentiment"]),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ CSV data from '{csv_file}' imported into 'is_project.review_sentiment'!")


def create_tripadvisor_attractions_cluster_table():
    """Create 'tripadvisor_attractions_cluster' table inside 'is_project' schema."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS is_project.tripadvisor_attractions_cluster (
            id SERIAL PRIMARY KEY,
            location_id NUMERIC,
            name TEXT,
            description TEXT,
            web_url TEXT,
            latitude NUMERIC,
            longitude NUMERIC,
            website TEXT,
            write_review TEXT,
            rating NUMERIC,
            rating_image_url TEXT,
            num_reviews NUMERIC,
            ranking_geo_location_id NUMERIC,
            ranking_string TEXT,
            geo_location_name TEXT,
            ranking_out_of NUMERIC,
            ranking_no NUMERIC,
            rating_1_review_count NUMERIC,
            rating_2_review_count NUMERIC,
            rating_3_review_count NUMERIC,
            rating_4_review_count NUMERIC,
            rating_5_review_count NUMERIC,
            tags TEXT,
            trip_types_solo NUMERIC,
            trip_types_couples NUMERIC,
            trip_types_business NUMERIC,
            trip_types_family NUMERIC,
            trip_types_friends NUMERIC,
            cleaned_tags TEXT,
            tag_embeddings TEXT,
            cluster NUMERIC
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'tripadvisor_attractions_cluster' ensured.")


def import_tripadvisor_attractions_cluster(csv_file):
    """Import data from CSV into 'tripadvisor_attractions_cluster'."""
    conn = connect_db()
    cursor = conn.cursor()
    
    df = pd.read_csv(csv_file)
    
    print(f"📥 Importing {len(df)} rows into 'is_project.tripadvisor_attractions_cluster'...")
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Progress", unit="row"):
        cursor.execute(
            """
            INSERT INTO is_project.tripadvisor_attractions_cluster (
                location_id, name, description, web_url, latitude, longitude, website, write_review,
                rating, rating_image_url, num_reviews, ranking_geo_location_id, ranking_string,
                geo_location_name, ranking_out_of, ranking_no, rating_1_review_count, rating_2_review_count,
                rating_3_review_count, rating_4_review_count, rating_5_review_count, tags, trip_types_solo,
                trip_types_couples, trip_types_business, trip_types_family, trip_types_friends, cleaned_tags,
                tag_embeddings, cluster
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                row["location_id"], row["name"], row["description"], row["web_url"],
                row["latitude"], row["longitude"], row["website"], row["write_review"],
                row["rating"], row["rating_image_url"], row["num_reviews"], row["ranking_geo_location_id"],
                row["ranking_string"], row["geo_location_name"], row["ranking_out_of"], row["ranking_no"],
                row["rating_1_review_count"], row["rating_2_review_count"], row["rating_3_review_count"],
                row["rating_4_review_count"], row["rating_5_review_count"], row["tags"],
                row["trip_types_solo"], row["trip_types_couples"], row["trip_types_business"],
                row["trip_types_family"], row["trip_types_friends"], row["cleaned_tags"],
                row["tag_embeddings"], row["cluster"]
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ CSV data from '{csv_file}' imported into 'is_project.tripadvisor_attractions_cluster'!")

def create_tat_attractions_table():
    """Create 'tat_attractions' table inside 'is_project' schema."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS is_project.tat_attractions (
            id SERIAL PRIMARY KEY,
            place_id TEXT,
            place_name_th TEXT,
            introduction_th TEXT,
            category_name TEXT,
            category_id NUMERIC,
            latitude NUMERIC,
            longitude NUMERIC,
            postcode NUMERIC,
            thumbnail_url TEXT,
            tags TEXT,
            province_id NUMERIC,
            province_name_th TEXT,
            district_id NUMERIC,
            district_name_th TEXT,
            sub_district_id NUMERIC,
            sub_district_name_th TEXT,
            updated_at TIMESTAMP,
            introduction_en TEXT,
            place_name_en TEXT,
            province_name_en TEXT,
            district_name_en TEXT,
            sub_district_name_en TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'tat_attractions' ensured.")


def import_tat_attractions(csv_file):
    """Import data from CSV into 'tat_attractions' with a progress bar."""
    conn = connect_db()
    cursor = conn.cursor()
    
    df = pd.read_csv(csv_file)

    print(f"📥 Importing {len(df)} rows into 'is_project.tat_attractions'...")
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Progress", unit="row"):
        cursor.execute(
            """
            INSERT INTO is_project.tat_attractions (
                place_id, place_name_th, introduction_th, category_name, category_id, latitude, longitude, postcode,
                thumbnail_url, tags, province_id, province_name_th, district_id, district_name_th, sub_district_id,
                sub_district_name_th, updated_at, introduction_en, place_name_en, province_name_en, district_name_en,
                sub_district_name_en
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                row["placeId"], row["place_name_th"], row["introduction_th"], row["category_name"], row["categoryId"],
                row["latitude"], row["longitude"], row["postcode"], row["thumbnail_url"], row["tags"], row["province_Id"],
                row["province_name_th"], row["district_Id"], row["district_name_th"], row["sub_district_Id"], row["sub_district_name_th"],
                row["updated_at"], row["introduction_en"], row["place_name_en"], row["province_name_en"], row["district_name_en"],
                row["sub_district_name_en"]
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ CSV data from '{csv_file}' imported successfully!")


if __name__ == "__main__":
    # ✅ Create schema and tables
    create_schema()
    # create_review_sentiment_table()
    # create_tripadvisor_attractions_cluster_table()
    create_tat_attractions_table() 

    # ✅ Import CSV files
    # import_review_sentiment("./test/prediction/SVN_Prediction.csv")
    # import_tripadvisor_attractions_cluster("./app/frontend//clustering_experiment/input/tag_embeddings.csv")
    import_tat_attractions("./app/frontend/merged_tat_attractions.csv")  

    print("🎉 All CSV data imported successfully!")
