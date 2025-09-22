import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.vector_store import VectorStoreService

def upload_products():
    """Upload all products to pgvector"""
    
    # Load products from JSON
    products_file = Path(__file__).parent.parent / 'data' / 'products.json'
    
    print(f"Loading products from: {products_file}")
    
    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Found {len(products)} products")
    
    # Initialize vector store
    print("🔧 Initializing vector store...")
    vector_store = VectorStoreService()
    
    # Upload products (bulk is faster)
    print(f"⬆Uploading {len(products)} products to pgvector...")
    
    # Upload in batches for progress tracking
    batch_size = 10
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        vector_store.add_products_bulk(batch)
        print(f"   Uploaded {min(i+batch_size, len(products))}/{len(products)}")
    
    print("All products uploaded successfully!")
    print(f"You can now search through {len(products)} products")

if __name__ == "__main__":
    upload_products()