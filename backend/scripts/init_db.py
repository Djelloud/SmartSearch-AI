import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Debug: Print the DATABASE_URL (hide password)
db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {db_url[:30]}...{db_url[-20:]}")  # Print partial URL
print(f"Full URL for debugging: {db_url}")  # Remove this after fixing

def initialize_database():
    """Initialize database with pgvector extension"""
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    with engine.connect() as conn:
        # Enable pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("✅ pgvector extension enabled")
        
        # Verify extension
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
        if result.fetchone():
            print("✅ pgvector verified successfully")
        else:
            print("❌ pgvector extension not found")

if __name__ == "__main__":
    initialize_database()