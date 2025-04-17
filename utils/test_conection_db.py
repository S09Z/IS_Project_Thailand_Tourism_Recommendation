import os
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_HOST = os.getenv("DB_POSTGRES_HOST")
DB_PORT = os.getenv("DB_POSTGRES_PORT", "5432")
DB_NAME = os.getenv("DB_POSTGRES_DATABASE")
DB_USER = os.getenv("DB_POSTGRES_USER")
DB_PASSWORD = os.getenv("DB_POSTGRES_PASSWORD")
DB_SCHEMA = os.getenv("DB_POSTGRES_SCHEMA")

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

@pytest.fixture
def db_connection():
    """Fixture to provide a database connection"""
    with engine.connect() as conn:
        yield conn  # Provide the connection to test functions

def test_database_connection(db_connection):
    """Test if the database connection to Neon PostgreSQL is successful"""
    result = db_connection.execute(text("SELECT 1;")).scalar()
    assert result == 1, "Database connection failed"
    
    
def test_load_data_from_neon(db_connection):
    """Test if the function successfully loads data from Neon PostgreSQL"""
    query = text(f"SELECT * FROM {DB_SCHEMA}.users LIMIT 5;")

    try:
        with db_connection as connection:
            df = pd.read_sql(query, connection)

        # Debug: Print DataFrame if empty
        if df.empty:
            pytest.fail("❌ Table exists but has NO DATA. Please insert test records.")

        # Assertions
        assert isinstance(df, pd.DataFrame), "Returned object is not a DataFrame"
        assert len(df) > 0, "No rows returned from database"
        print(df.head())

    except Exception as e:
        pytest.fail(f"Database query failed: {e}")
