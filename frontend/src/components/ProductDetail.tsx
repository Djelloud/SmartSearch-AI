import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { productApi } from '../services/api';
import { Product, SearchResult } from '../types/product';
import ProductCard from './ProductCard';

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      
      try {
        const productData = await productApi.getProduct(id);
        setProduct(productData);
        
        const recsData = await productApi.getRecommendations(id);
        setRecommendations(recsData.recommendations);
      } catch (error) {
        console.error('Error fetching product:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!product) return <div>Product not found</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center">
          <img src={product.image_url || 'https://placehold.co/400x400'} alt={product.name} />
        </div>
        
        <div>
          <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
          <p className="text-2xl text-blue-600 mb-4">${product.price}</p>
          <p className="text-gray-600 mb-6">{product.description}</p>
          
          <div className="space-y-2">
            <p><strong>Category:</strong> {product.category}</p>
            <p><strong>Brand:</strong> {product.brand}</p>
            <p><strong>Rating:</strong> {product.rating}/5</p>
            <p><strong>In Stock:</strong> {product.stock} units</p>
          </div>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4">Similar Products</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {recommendations.map(({ product, score }) => (
            <ProductCard key={product.id} product={product} score={score} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;