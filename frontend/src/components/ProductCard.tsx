import React from 'react';
import { Star, Package } from 'lucide-react';
import { Product } from '../types/product';

interface ProductCardProps {
  product: Product;
  score?: number;
  onClick?: () => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, score, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
    >
      <div className="aspect-square bg-gray-200 flex items-center justify-center">
        {product.image_url ? (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <Package className="w-24 h-24 text-gray-400" />
        )}
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 line-clamp-2">
          {product.name}
        </h3>
        
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {product.description}
        </p>
        
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-bold text-blue-600">
            ${product.price.toFixed(2)}
          </span>
          
          {product.rating && (
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-medium">{product.rating}</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">{product.brand}</span>
          {score !== undefined && (
            <span className="text-green-600 font-medium">
              {(score * 100).toFixed(0)}% match
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;