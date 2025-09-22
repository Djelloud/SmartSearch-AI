import { useState } from 'react';
import SearchBar from './components/SearchBar';
import ProductCard from './components/ProductCard';
import { productApi } from './services/api';
import { SearchResult } from './types/product';

function App() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setSearchQuery(query);
    
    try {
      const response = await productApi.search(query);
      setResults(response.results);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Make sure the backend is running!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Product Search
          </h1>
          <p className="text-gray-600 mt-1">
            Find products using natural language
          </p>
        </div>
      </header>

      {/* Search Section */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Searching...</p>
          </div>
        )}

        {/* Results */}
        {!isLoading && results.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Results for "{searchQuery}"
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {results.map(({ product, score }) => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  score={score}
                  onClick={() => console.log('View product:', product.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && results.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <p className="text-gray-600">No results found for "{searchQuery}"</p>
          </div>
        )}

        {/* Initial State */}
        {!isLoading && !searchQuery && (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">
              Try searching for "wireless headphones" or "fitness tracker"
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {['headphones', 'camera', 'office chair', 'green tea'].map((term) => (
                <button
                  key={term}
                  onClick={() => handleSearch(term)}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-full text-sm transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;