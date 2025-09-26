from fastapi import APIRouter, HTTPException
from app.models import SearchQuery, SearchResponse, SearchResult
from app.services.search_service import SearchService
from typing import Optional
import time

router = APIRouter()
search_service = SearchService() 

@router.post("", response_model=SearchResponse)
async def semantic_search(
    query: SearchQuery,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
):
    """Semantic search with filters"""
    start_time = time.time()
    
    try:
        # Get search results
        results = await search_service.search(query.query, query.limit * 2)
        
        # Apply filters
        filtered_results = []
        for result in results:
            product = result.product
            
            # Category filter
            if category and product.category.lower() != category.lower():
                continue
            
            # Price filters
            if min_price and product.price < min_price:
                continue
            if max_price and product.price > max_price:
                continue
            
            # Rating filter
            if min_rating and (not product.rating or product.rating < min_rating):
                continue
            
            filtered_results.append(result)
        
        # Limit results
        filtered_results = filtered_results[:query.limit]
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=query.query,
            results=filtered_results,
            total=len(filtered_results),
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{product_id}")
async def get_recommendations(product_id: str, limit: int = 5):
    """
    Get similar product recommendations
    """
    try:
        recommendations = await search_service.get_similar(product_id, limit)
        return {"product_id": product_id, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))