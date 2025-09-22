from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    """Product model matching your mock data structure"""
    id: str
    name: str
    description: str
    category: str
    price: float
    brand: str
    image_url: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    stock: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "PROD001",
                "name": "Wireless Bluetooth Headphones",
                "description": "Premium noise-cancelling headphones with 30-hour battery life",
                "category": "Electronics",
                "price": 149.99,
                "brand": "TechSound",
                "rating": 4.5,
                "stock": 50
            }
        }

class SearchQuery(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=50)
    
class SearchResult(BaseModel):
    """Search response with relevance score"""
    product: Product
    score: float = Field(..., ge=0, le=1)
    
class SearchResponse(BaseModel):
    """Search results wrapper"""
    query: str
    results: List[SearchResult]
    total: int
    processing_time: float