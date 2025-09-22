from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Product
import json
import os

router = APIRouter()

# Load mock products (you'll create this file on Day 1)
def load_products():
    """Load products from JSON file"""
    data_path = os.path.join(os.path.dirname(__file__), "../../data/products.json")
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

PRODUCTS = load_products()

@router.get("/", response_model=List[Product])
async def get_all_products(skip: int = 0, limit: int = 20):
    """Get all products with pagination"""
    return PRODUCTS[skip : skip + limit]

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get single product by ID"""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/category/{category}", response_model=List[Product])
async def get_products_by_category(category: str):
    """Get products by category"""
    filtered = [p for p in PRODUCTS if p.get("category", "").lower() == category.lower()]
    return filtered