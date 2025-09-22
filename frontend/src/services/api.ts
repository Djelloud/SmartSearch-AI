import axios from 'axios';
import { Product, SearchResponse, RecommendationsResponse } from '../types/product';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productApi = {
  // Get all products
  getAllProducts: async (skip = 0, limit = 20): Promise<Product[]> => {
    const response = await api.get(`/products?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get single product
  getProduct: async (id: string): Promise<Product> => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Get products by category
  getProductsByCategory: async (category: string): Promise<Product[]> => {
    const response = await api.get(`/products/category/${category}`);
    return response.data;
  },

  // Semantic search
  search: async (query: string, limit = 10): Promise<SearchResponse> => {
    const response = await api.post('/search', { query, limit });
    return response.data;
  },

  // Get recommendations
  getRecommendations: async (productId: string, limit = 5): Promise<RecommendationsResponse> => {
    const response = await api.get(`/search/recommendations/${productId}?limit=${limit}`);
    return response.data;
  },
};

export default api;