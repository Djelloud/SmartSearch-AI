import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import ProductCard from './components/ProductCard';
import SearchFilters from './components/SearchFilters';
import { productApi } from './services/api';
import { SearchResult } from './types/product';
import { History, AlertCircle, Grid, List, SlidersHorizontal } from 'lucide-react';

function App() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    minPrice: '',
    maxPrice: '',
    minRating: ''
  });

  // Load search history on component mount
  useEffect(() => {
    setSearchHistory(getSearchHistory());
  }, []);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setSearchQuery(query);
    setError(null);
    setShowFilters(true); // Show filters after search
    
    try {
      const response = await productApi.search(query, 24, filters); // More products
      setResults(response.results);
      
      // Save to search history
      saveSearchHistory(query);
      setSearchHistory(getSearchHistory());
      
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please check if the backend is running.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    // Re-search with new filters if there's an active query
    if (searchQuery) {
      handleSearch(searchQuery);
    }
  };

  const handleHistorySearch = (query: string) => {
    handleSearch(query);
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm shadow-sm border-b border-gray-200">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-1">
                SmartSearch-AI
              </h1>
              <p className="text-gray-600 text-sm lg:text-base">
                Semantic product search using AI-powered vector embeddings
              </p>
            </div>
            
            {/* View Toggle (only show when there are results) */}
            {results.length > 0 && (
              <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid' 
                      ? 'bg-white shadow-sm text-blue-600' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list' 
                      ? 'bg-white shadow-sm text-blue-600' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Content Area with Sidebar Layout for Search Results */}
        {searchQuery ? (
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar with Filters */}
            <aside className="lg:w-80 flex-shrink-0 order-2 lg:order-1">
              <div className="sticky top-24">
                {/* Results Summary */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className="text-lg font-semibold text-gray-900">Search Results</h2>
                    {!isLoading && results.length > 0 && (
                      <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                        {results.length} found
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Showing results for: <span className="font-medium text-gray-900">"{searchQuery}"</span>
                  </p>
                  
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg transition-colors ${
                      showFilters 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <SlidersHorizontal className="w-4 h-4" />
                    {showFilters ? 'Hide Filters' : 'Show Filters'}
                  </button>
                </div>

                {/* Filters */}
                {showFilters && (
                  <div className="animate-slide-up">
                    <SearchFilters onFilterChange={handleFilterChange} />
                  </div>
                )}
              </div>
            </aside>

            {/* Main Results Area */}
            <div className="flex-1 order-1 lg:order-2">
              {/* Error Message */}
              {error && (
                <ErrorMessage message={error} onClose={clearError} />
              )}

              {/* Loading State */}
              {isLoading && (
                <div className={
                  viewMode === 'grid' 
                    ? "grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6" 
                    : "space-y-4"
                }>
                  {Array.from({ length: 8 }).map((_, index) => (
                    <SkeletonCard key={index} />
                  ))}
                </div>
              )}

              {/* Results */}
              {!isLoading && results.length > 0 && (
                <div className={
                  viewMode === 'grid' 
                    ? "grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 animate-fade-in" 
                    : "space-y-4 animate-fade-in"
                }>
                  {results.map(({ product, score }) => (
                    <ProductCard 
                      key={product.id} 
                      product={product} 
                      score={score}
                      onClick={() => {
                        console.log('View product:', product.id);
                        // TODO: Navigate to product detail page
                      }}
                    />
                  ))}
                </div>
              )}

              {/* Empty State */}
              {!isLoading && results.length === 0 && !error && (
                <div className="text-center py-16 animate-fade-in">
                  <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-6" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No results found for "{searchQuery}"
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Try adjusting your search terms or filters
                  </p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {['headphones', 'camera', 'office chair', 'fitness tracker'].map((term) => (
                      <button
                        key={term}
                        onClick={() => handleSearch(term)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        Try "{term}"
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          // Initial State Layout
          <div className="space-y-12">
            {/* Welcome Section */}
            <div className="text-center py-8">
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
                Discover Products with AI Search
              </h2>
              <p className="text-xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
                Experience the power of semantic search. Use natural language to find exactly what you need.
              </p>
            </div>

            {/* Centered Search Section */}
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
                <SearchBar onSearch={handleSearch} isLoading={isLoading} />
              </div>
            </div>

            {/* Search History */}
            {searchHistory.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <History className="w-5 h-5 text-gray-500" />
                  <h3 className="text-lg font-medium text-gray-900">Recent Searches</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {searchHistory.map((query, index) => (
                    <button
                      key={index}
                      onClick={() => handleHistorySearch(query)}
                      className="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 hover:text-blue-800 rounded-full text-sm border border-blue-200 hover:border-blue-300 transition-all duration-200 shadow-sm hover:shadow-md"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Sample Searches */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">Try these intelligent searches:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { query: 'gift for fitness enthusiast', description: 'Smart fitness tracker, yoga mat', icon: '🏃‍♂️' },
                  { query: 'eco-friendly home products', description: 'Sustainable living items', icon: '🌱' },
                  { query: 'budget tech under $100', description: 'Affordable electronics', icon: '💻' },
                  { query: 'premium office setup', description: 'High-end work equipment', icon: '🏢' },
                  { query: 'healthy cooking essentials', description: 'Kitchen tools for wellness', icon: '🥗' },
                  { query: 'travel gear for backpacking', description: 'Portable adventure items', icon: '🎒' }
                ].map((item) => (
                  <button
                    key={item.query}
                    onClick={() => handleSearch(item.query)}
                    className="group p-6 bg-gradient-to-br from-gray-50 to-blue-50 hover:from-blue-50 hover:to-blue-100 rounded-xl border border-gray-200 hover:border-blue-300 transition-all duration-300 shadow-sm hover:shadow-lg text-left transform hover:-translate-y-1"
                  >
                    <div className="text-3xl mb-3">{item.icon}</div>
                    <div className="font-semibold text-blue-700 group-hover:text-blue-800 mb-2 transition-colors">
                      "{item.query}"
                    </div>
                    <div className="text-sm text-gray-600 group-hover:text-gray-700 transition-colors">
                      {item.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Features Showcase */}
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow duration-300">
                <div className="text-5xl mb-6 text-center">🧠</div>
                <h4 className="text-xl font-semibold text-gray-900 mb-4 text-center">Semantic Understanding</h4>
                <p className="text-gray-600 text-center leading-relaxed">
                  Our AI understands context and meaning, not just keywords. Search naturally and find what you really want.
                </p>
              </div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow duration-300">
                <div className="text-5xl mb-6 text-center">⚡</div>
                <h4 className="text-xl font-semibold text-gray-900 mb-4 text-center">Lightning Fast</h4>
                <p className="text-gray-600 text-center leading-relaxed">
                  Vector similarity search powered by pgvector delivers relevant results in under 200ms.
                </p>
              </div>
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow duration-300">
                <div className="text-5xl mb-6 text-center">🎯</div>
                <h4 className="text-xl font-semibold text-gray-900 mb-4 text-center">Smart Matching</h4>
                <p className="text-gray-600 text-center leading-relaxed">
                  Advanced algorithms provide relevance scores and intelligent filtering for perfect matches.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// Helper Components
const SkeletonCard = () => (
  <div className="bg-white rounded-xl shadow-sm p-4 animate-pulse border border-gray-100">
    <div className="aspect-square bg-gray-200 rounded-lg mb-4"></div>
    <div className="h-4 bg-gray-200 rounded mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
    <div className="flex justify-between items-center">
      <div className="h-6 bg-gray-200 rounded w-1/3"></div>
      <div className="h-8 bg-gray-200 rounded w-20"></div>
    </div>
  </div>
);

const ErrorMessage = ({ message, onClose }: { message: string, onClose?: () => void }) => (
  <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center justify-between">
    <div className="flex items-center gap-3">
      <AlertCircle className="w-5 h-5 text-red-500" />
      <p className="text-red-700 font-medium">{message}</p>
    </div>
    {onClose && (
      <button
        onClick={onClose}
        className="text-red-500 hover:text-red-700 text-xl"
      >
        ×
      </button>
    )}
  </div>
);

// Helper Functions
const saveSearchHistory = (query: string) => {
  const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
  const updated = [query, ...history.filter((q: string) => q !== query)].slice(0, 5);
  localStorage.setItem('searchHistory', JSON.stringify(updated));
};

const getSearchHistory = (): string[] => {
  return JSON.parse(localStorage.getItem('searchHistory') || '[]');
};

export default App;