#!/usr/bin/env python3
"""
Simple test runner script that handles the Python path correctly
Run this from the backend directory: python3 run_tests.py

Note: Use python3 (not python.exe) in WSL environment
"""

import sys
import os
from pathlib import Path
import asyncio
import argparse

def main():
    # Ensure we're in the backend directory
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir
    tests_dir = backend_dir / "tests"
    
    # Add directories to Python path
    sys.path.insert(0, str(backend_dir))
    sys.path.insert(0, str(tests_dir))
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print(f"Running tests from: {backend_dir}")
    print(f"Tests directory: {tests_dir}")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="SmartSearch-AI Testing Suite")
    parser.add_argument("--environment", "-e", choices=["development", "staging", "production"], 
                       default="development", help="Test environment")
    parser.add_argument("--advanced", "-a", action="store_true", 
                       help="Run advanced tests with detailed metrics")
    parser.add_argument("--benchmark", "-b", action="store_true", 
                       help="Run continuous benchmarking")
    
    args = parser.parse_args()
    
    try:
        # Import the test runner
        from tests.test_runner import TestRunner
        
        # Create and run the test runner
        runner = TestRunner(environment=args.environment, advanced=args.advanced)
        
        print(f"SmartSearch-AI Testing Suite v2.0")
        print(f"Environment: {args.environment.upper()}")
        print(f"Advanced Mode: {args.advanced}")
        print("This will evaluate your semantic search accuracy and performance\n")
        
        async def run_tests():
            try:
                if args.benchmark:
                    # Run continuous benchmarking
                    from tests.rag_test_framework import ContinuousBenchmark
                    benchmark = ContinuousBenchmark()
                    await benchmark.run_benchmark()
                else:
                    # Run full evaluation
                    accuracy_results, gates_passed = await runner.run_full_evaluation()
                    
                    print(f"\n✅ Testing completed successfully!")
                    
                    # Exit with appropriate code for CI
                    if not gates_passed:
                        print(f"❌ Quality gates failed for {args.environment} environment")
                        return 1
                
            except Exception as e:
                print(f"\n❌ Testing failed: {e}")
                import traceback
                traceback.print_exc()
                return 1
            
            return 0
        
        # Run the async function
        exit_code = asyncio.run(run_tests())
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have all required dependencies installed:")
        print("  pip install -r requirements.txt")
        print("\nAlso ensure the backend services are properly set up.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
