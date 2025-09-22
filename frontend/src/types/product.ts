export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  brand: string;
  image_url?: string;
  rating?: number;
  stock: number;
}

export interface SearchResult {
  product: Product;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  processing_time: number;
}

export interface RecommendationsResponse {
  product_id: string;
  recommendations: SearchResult[];
}