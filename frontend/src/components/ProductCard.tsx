import React from 'react';
import { Star, Package, ShoppingCart, Heart } from 'lucide-react';
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
      className="group bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1"
    >
      {/* Image Container */}
      <div className="relative aspect-square bg-gradient-to-br from-gray-50 to-gray-100 overflow-hidden">
        {product.image_url ? (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.nextElementSibling?.classList.remove('hidden');
            }}
          />
        ) : null}
        <div className="hidden absolute inset-0 flex items-center justify-center">
          <Package className="w-16 h-16 text-gray-300" />
        </div>
        
        {/* Score Badge */}
        {score !== undefined && (
          <div className="absolute top-3 right-3 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold shadow-lg">
            {(score * 100).toFixed(0)}% match
          </div>
        )}
        
        {/* Quick Actions */}
        <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <button className="bg-white/80 backdrop-blur-sm p-2 rounded-full hover:bg-white shadow-lg transition-colors">
            <Heart className="w-4 h-4 text-gray-600 hover:text-red-500" />
          </button>
        </div>
        
        {/* Stock Status */}
        {product.stock < 10 && (
          <div className="absolute bottom-3 left-3 bg-red-500 text-white px-2 py-1 rounded text-xs font-medium">
            Only {product.stock} left
          </div>
        )}
      </div>
      
      {/* Content */}
      <div className="p-5">
        {/* Category */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
            {product.category}
          </span>
          <span className="text-xs text-gray-500 font-medium">
            {product.brand}
          </span>
        </div>
        
        {/* Product Name */}
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
          {product.name}
        </h3>
        
        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-2 leading-relaxed">
          {product.description}
        </p>
        
        {/* Rating */}
        {product.rating && (
          <div className="flex items-center gap-1 mb-3">
            <div className="flex items-center">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star 
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(product.rating!) 
                      ? 'text-yellow-400 fill-yellow-400' 
                      : i < product.rating! 
                        ? 'text-yellow-400 fill-yellow-200'
                        : 'text-gray-200'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm font-medium text-gray-700 ml-1">
              {product.rating.toFixed(1)}
            </span>
            <span className="text-xs text-gray-500 ml-1">
              ({Math.floor(Math.random() * 500) + 50} reviews)
            </span>
          </div>
        )}
        
        {/* Price and Action */}
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-2xl font-bold text-gray-900">
              ${product.price.toFixed(2)}
            </span>
            {product.price > 100 && (
              <span className="text-sm text-green-600 font-medium">
                Free shipping
              </span>
            )}
          </div>
          
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2 shadow-md hover:shadow-lg">
            <ShoppingCart className="w-4 h-4" />
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;