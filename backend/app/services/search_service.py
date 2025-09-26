from typing import List
from app.models import SearchResult, Product
from app.services.vector_store import VectorStoreService
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """Search service using pgvector for semantic search"""
    
    def __init__(self):
        self.vector_store = VectorStoreService()
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Perform semantic search using pgvector
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects with products and scores
        """
        try:
            # Perform vector similarity search
            results = self.vector_store.search(query, limit)
            
            # Convert to SearchResult objects
            search_results = []
            for doc, distance in results:
                # pgvector returns distance (lower is better)
                # Convert to similarity score (0-1, higher is better)
                similarity_score = 1 - distance
                
                # Extract product from metadata
                product_data = doc.metadata
                product = Product(**product_data)
                
                search_results.append(SearchResult(
                    product=product,
                    score=similarity_score
                ))
            
            logger.info(f"Search for '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    async def get_similar(self, product_id: str, limit: int = 5) -> List[SearchResult]:
        """
        Get similar products based on product ID
        
        Args:
            product_id: ID of the product to find similar items for
            limit: Maximum number of results
            
        Returns:
            List of similar products
        """
        try:
            # Search using product ID as query
            # In a real system, you'd fetch the product and use its embedding
            results = self.vector_store.search(product_id, limit + 1)
            
            # Filter out the original product and convert results
            search_results = []
            for doc, distance in results:
                if doc.metadata.get('id') != product_id:
                    similarity_score = 1 / (1 + distance)
                    product = Product(**doc.metadata)
                    search_results.append(SearchResult(
                        product=product,
                        score=similarity_score
                    ))
            
            return search_results[:limit]
            
        except Exception as e:
            logger.error(f"Similar products error: {str(e)}")
            return []
    
    async def initialize_vector_store(self, products: List[dict]):

        pass
    async def get_similar(self, product_id: str, limit: int = 5) -> List[SearchResult]:
        """Get similar products based on product ID"""
        try:
            # Get the product from database
            # For now, simulate by getting product embedding
            results = self.vector_store.search(product_id, limit + 1)
            
            # Filter out the original product
            search_results = []
            for doc, score in results:
                if doc.metadata.get('id') != product_id:
                    similarity_score = 1 / (1 + score)
                    product = Product(**doc.metadata)
                    search_results.append(SearchResult(
                        product=product,
                        score=similarity_score
                    ))
            
            return search_results[:limit]
        except Exception as e:
            logger.error(f"Recommendations error: {str(e)}")
            return []