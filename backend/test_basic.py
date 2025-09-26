#!/usr/bin/env python3
"""
Basic test to verify the system is working
Run this first to check if your setup is correct: python3 test_basic.py

Note: Use python3 (not python.exe) in WSL environment
"""

import sys
import os
from pathlib import Path
import asyncio

def main():
    # Setup paths
    backend_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)
    
    print("🔍 SmartSearch-AI Basic System Test")
    print("=" * 50)
    
    try:
        print("1. Testing imports...")
        from app.services.search_service import SearchService
        from app.models import SearchResult
        print("   ✅ Backend imports successful")
        
        print("\n2. Testing search service initialization...")
        search_service = SearchService()
        print("   ✅ SearchService initialized")
        
        print("\n3. Testing basic search...")
        
        async def test_search():
            try:
                results = await search_service.search("headphones", 5)
                print(f"   ✅ Search completed - found {len(results)} results")
                
                if results:
                    print(f"\n   Sample result:")
                    result = results[0]
                    print(f"   - Product: {result.product.name}")
                    print(f"   - Score: {result.score:.3f}")
                    print(f"   - Category: {result.product.category}")
                else:
                    print("   ⚠️  No results found - this might indicate an issue with the data or embeddings")
                
                return True
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                return False
        
        # Run the async test
        search_success = asyncio.run(test_search())
        
        print(f"\n{'='*50}")
        if search_success:
            print("🎉 Basic system test PASSED!")
            print("You can now run the full test suite:")
            print("   python run_tests.py")
            print("   python run_tests.py --advanced")
        else:
            print("❌ Basic system test FAILED!")
            print("Please check:")
            print("1. Database is running and contains data")
            print("2. Search service is properly configured")
            print("3. Embeddings are generated for products")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running from the backend directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check if the backend app structure is correct")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
