from langchain_postgres import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VectorStoreService:
    """Service for vector similarity search using pgvector"""
    
    def __init__(self):
        # Database connection string
        self.connection = os.getenv("DATABASE_URL")
        
        # Initialize embedding model
        use_local = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
        
        if use_local:
            print("📦 Loading local embedding model (sentence-transformers)...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Local embeddings loaded (dimension: 384)")
        else:
            print("🔑 Using OpenAI embeddings...")
            self.embeddings = OpenAIEmbeddings()
            print("✅ OpenAI embeddings configured (dimension: 1536)")
        
        # Initialize PGVector store
        self.vectorstore = PGVector(
            connection=self.connection,
            embeddings=self.embeddings,
            collection_name="products",
            use_jsonb=True,
            pre_delete_collection=False
        )
        print("✅ Vector store initialized")
    
    def add_product(self, product: dict):
        """Add a single product to the vector store"""
        # Create searchable text combining important fields
        text = (
            f"{product['name']} "
            f"{product['description']} "
            f"Category: {product['category']} "
            f"Brand: {product['brand']}"
        )
        
        # Add to vector store with metadata
        self.vectorstore.add_texts(
            texts=[text],
            metadatas=[product],
            ids=[product['id']]
        )
    
    def add_products_bulk(self, products: List[dict]):
        """Add multiple products efficiently"""
        texts = []
        metadatas = []
        ids = []
        
        for product in products:
            text = (
                f"{product['name']} "
                f"{product['description']} "
                f"Category: {product['category']} "
                f"Brand: {product['brand']}"
            )
            texts.append(text)
            metadatas.append(product)
            ids.append(product['id'])
        
        self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[Any, float]]:
        """Search for products similar to query"""
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=limit
        )
        return results
    
    def search_by_embedding(self, embedding: List[float], limit: int = 10) -> List[Tuple[Any, float]]:
        """Search using a pre-computed embedding"""
        results = self.vectorstore.similarity_search_by_vector_with_relevance_scores(
            embedding=embedding,
            k=limit
        )
        return results
    
    def get_product_count(self) -> int:
        """Get total number of products in vector store"""
        # This is a simple check - in production you'd query the actual table
        return 0  # Will be updated after upload