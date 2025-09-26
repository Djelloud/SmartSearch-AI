import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
import sys
from pathlib import Path

# Add the backend directory to Python path if not already there
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from app.services.search_service import SearchService
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Make sure you're running from the backend directory and the backend is properly set up")
    raise

class PerformanceTestSuite:
    """Performance testing for semantic search"""
    
    def __init__(self):
        self.search_service = SearchService()
    
    async def test_response_time(self):
        """Test search response time under normal load"""
        queries = [
            "wireless headphones",
            "fitness tracker",
            "office chair",
            "kitchen appliances",
            "running shoes"
        ]
        
        times = []
        for query in queries:
            start = time.time()
            await self.search_service.search(query, 10)
            end = time.time()
            times.append(end - start)
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        print(f"Average response time: {avg_time:.3f}s")
        print(f"95th percentile: {p95_time:.3f}s")
        
        # Assertions for acceptable performance
        assert avg_time < 0.5, f"Average response time too slow: {avg_time:.3f}s"
        assert p95_time < 1.0, f"95th percentile too slow: {p95_time:.3f}s"
        
        return times
    
    async def test_concurrent_load(self):
        """Test performance under concurrent load"""
        async def search_task(query):
            start = time.time()
            await self.search_service.search(f"{query} test", 5)
            return time.time() - start
        
        # Simulate 20 concurrent searches
        tasks = [search_task(f"query{i}") for i in range(20)]
        times = await asyncio.gather(*tasks)
        
        avg_concurrent_time = statistics.mean(times)
        print(f"Average time under 20x concurrent load: {avg_concurrent_time:.3f}s")
        
        # Should handle concurrency reasonably well
        assert avg_concurrent_time < 2.0, f"Concurrent performance too slow: {avg_concurrent_time:.3f}s"
        
        return times
    
    async def test_memory_usage(self):
        """Monitor memory usage during operations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple searches
        for i in range(50):
            await self.search_service.search(f"test query {i}", 10)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        # Memory shouldn't grow excessively
        assert memory_increase < 100, f"Memory leak detected: +{memory_increase:.1f}MB"
        
        return memory_increase

@pytest.mark.asyncio
class TestPerformance:
    
    @pytest.fixture
    def perf_suite(self):
        return PerformanceTestSuite()
    
    async def test_response_times(self, perf_suite):
        times = await perf_suite.test_response_time()
        assert all(t < 1.0 for t in times), "Some queries took too long"
    
    async def test_concurrent_performance(self, perf_suite):
        times = await perf_suite.test_concurrent_load()
        # Most requests should still be reasonably fast
        fast_requests = sum(1 for t in times if t < 1.0)
        assert fast_requests >= len(times) * 0.8, "Too many slow requests under load"
    
    async def test_memory_efficiency(self, perf_suite):
        memory_increase = await perf_suite.test_memory_usage()
        assert memory_increase < 50, "Memory usage too high"