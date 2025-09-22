from fastapi import APIRouter, HTTPException
from app.models import SearchQuery, SearchResponse, SearchResult
from app.services.search_service import SearchService
import time

router = APIRouter()
search_service = SearchService() 

@router.post("", response_model=SearchResponse)
async def semantic_search(query: SearchQuery):
    """
    Perform semantic search using LangChain and vector embeddings
    """
    start_time = time.time()
    
    try:
        # TODO: 
        results = await search_service.search(
            query=query.query,
            limit=query.limit
        )
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=query.query,
            results=results,
            total=len(results),
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