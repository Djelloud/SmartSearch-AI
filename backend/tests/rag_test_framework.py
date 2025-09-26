import pytest
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
import json
import logging
from datetime import datetime
import sys
import os
from pathlib import Path

# Add the backend directory to Python path if not already there
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from app.services.search_service import SearchService
    from app.models import SearchResult
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Make sure you're running from the backend directory and the backend is properly set up")
    raise

@dataclass
class TestCase:
    query: str
    expected_categories: List[str]
    expected_keywords: List[str]
    min_score_threshold: float = 0.3
    min_results: int = 1
    max_results: int = 10
    description: str = ""

@dataclass
class EvalResult:
    query: str
    passed: bool
    score: float
    precision: float
    category_match: bool
    keyword_match: bool
    results_count: int
    top_result: str
    errors: List[str]
    execution_time: float

class RAGEvaluator:
    """Comprehensive evaluation framework for semantic search"""
    
    def __init__(self):
        self.search_service = SearchService()
        self.test_results = []
        
    async def evaluate_single_query(self, test_case: TestCase) -> EvalResult:
        """Evaluate a single search query"""
        start_time = datetime.now()
        errors = []
        
        try:
            # Perform search
            results = await self.search_service.search(test_case.query, test_case.max_results)
            
            # Calculate metrics
            category_match = self._check_category_relevance(results, test_case.expected_categories)
            keyword_match = self._check_keyword_relevance(results, test_case.expected_keywords)
            avg_score = sum(r.score for r in results) / len(results) if results else 0
            
            # Determine pass/fail
            passed = (
                len(results) >= test_case.min_results and
                avg_score >= test_case.min_score_threshold and
                (category_match or keyword_match)
            )
            
            if not passed:
                if len(results) < test_case.min_results:
                    errors.append(f"Insufficient results: {len(results)} < {test_case.min_results}")
                if avg_score < test_case.min_score_threshold:
                    errors.append(f"Low relevance: {avg_score:.3f} < {test_case.min_score_threshold}")
                if not category_match and not keyword_match:
                    errors.append("No category or keyword matches found")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return EvalResult(
                query=test_case.query,
                passed=passed,
                score=avg_score,
                precision=self._calculate_precision(results, test_case),
                category_match=category_match,
                keyword_match=keyword_match,
                results_count=len(results),
                top_result=results[0].product.name if results else "No results",
                errors=errors,
                execution_time=execution_time
            )
            
        except Exception as e:
            return EvalResult(
                query=test_case.query,
                passed=False,
                score=0.0,
                precision=0.0,
                category_match=False,
                keyword_match=False,
                results_count=0,
                top_result="ERROR",
                errors=[str(e)],
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _check_category_relevance(self, results: List[SearchResult], expected_categories: List[str]) -> bool:
        """Check if results match expected categories"""
        if not results or not expected_categories:
            return False
        
        result_categories = [r.product.category.lower() for r in results[:3]]  # Top 3
        expected_lower = [cat.lower() for cat in expected_categories]
        
        # At least one of top 3 results should match expected categories
        return any(cat in expected_lower for cat in result_categories)
    
    def _check_keyword_relevance(self, results: List[SearchResult], expected_keywords: List[str]) -> bool:
        """Check if results contain expected keywords"""
        if not results or not expected_keywords:
            return False
        
        # Check top result's name and description
        top_result = results[0].product
        text = f"{top_result.name} {top_result.description}".lower()
        
        return any(keyword.lower() in text for keyword in expected_keywords)
    
    def _calculate_precision(self, results: List[SearchResult], test_case: TestCase) -> float:
        """Calculate precision based on category and keyword matches"""
        if not results:
            return 0.0
        
        relevant_count = 0
        for result in results[:5]:  # Top 5 for precision
            product = result.product
            text = f"{product.name} {product.description} {product.category}".lower()
            
            # Check if relevant based on categories or keywords
            category_relevant = any(cat.lower() in product.category.lower() for cat in test_case.expected_categories)
            keyword_relevant = any(kw.lower() in text for kw in test_case.expected_keywords)
            
            if category_relevant or keyword_relevant:
                relevant_count += 1
        
        return relevant_count / min(len(results), 5)

# Test Cases Definition
TEST_CASES = [
    # Exact product matches
    TestCase(
        query="wireless headphones",
        expected_categories=["Electronics", "Audio"],
        expected_keywords=["headphone", "wireless", "bluetooth", "audio"],
        min_score_threshold=0.6,
        description="Direct product search"
    ),
    
    # Intent-based searches
    TestCase(
        query="gift for fitness enthusiast",
        expected_categories=["Sports", "Electronics", "Health"],
        expected_keywords=["fitness", "tracker", "watch", "exercise", "workout", "gym"],
        min_score_threshold=0.4,
        description="Intent-based semantic search"
    ),
    
    # Lifestyle/use-case searches
    TestCase(
        query="work from home setup",
        expected_categories=["Furniture", "Electronics", "Office"],
        expected_keywords=["chair", "desk", "monitor", "keyboard", "office", "ergonomic"],
        min_score_threshold=0.4,
        description="Lifestyle-based search"
    ),
    
    # Price-conscious searches
    TestCase(
        query="budget electronics under 100",
        expected_categories=["Electronics"],
        expected_keywords=["electronic", "device", "tech"],
        min_score_threshold=0.3,
        description="Price-sensitive search"
    ),
    
    # Eco-friendly searches
    TestCase(
        query="eco-friendly kitchen products",
        expected_categories=["Home & Garden", "Food & Beverage"],
        expected_keywords=["eco", "organic", "sustainable", "kitchen", "cooking"],
        min_score_threshold=0.3,
        description="Values-based search"
    ),
    
    # Synonym handling
    TestCase(
        query="mobile phone",
        expected_categories=["Electronics"],
        expected_keywords=["phone", "mobile", "smartphone", "cell"],
        min_score_threshold=0.5,
        description="Synonym recognition"
    ),
    
    # Complex descriptive searches
    TestCase(
        query="comfortable chair for long hours coding",
        expected_categories=["Furniture"],
        expected_keywords=["chair", "office", "ergonomic", "comfortable", "desk"],
        min_score_threshold=0.4,
        description="Complex descriptive search"
    ),
    
    # Edge case: very specific
    TestCase(
        query="japanese green tea matcha powder",
        expected_categories=["Food & Beverage"],
        expected_keywords=["tea", "green", "matcha", "japanese", "organic"],
        min_score_threshold=0.4,
        description="Highly specific product search"
    )
]

class TestSemanticSearch:
    """Pytest test class for semantic search evaluation"""
    
    @pytest.fixture
    def evaluator(self):
        return RAGEvaluator()
    
    @pytest.mark.asyncio
    async def test_all_queries(self, evaluator):
        """Run all test cases and generate report"""
        results = []
        
        for test_case in TEST_CASES:
            result = await evaluator.evaluate_single_query(test_case)
            results.append(result)
            
            # Individual test assertions
            assert result.results_count >= test_case.min_results, f"Query '{test_case.query}' returned too few results"
            assert result.score >= test_case.min_score_threshold, f"Query '{test_case.query}' score too low: {result.score}"
        
        # Generate comprehensive report
        self._generate_report(results)
        
        # Overall pass rate assertion
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        assert pass_rate >= 0.7, f"Overall pass rate too low: {pass_rate:.1%}"
    
    def _generate_report(self, results: List[EvalResult]):
        """Generate detailed evaluation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "average_score": sum(r.score for r in results) / len(results),
            "average_precision": sum(r.precision for r in results) / len(results),
            "average_execution_time": sum(r.execution_time for r in results) / len(results),
            "results": [
                {
                    "query": r.query,
                    "passed": r.passed,
                    "score": round(r.score, 3),
                    "precision": round(r.precision, 3),
                    "top_result": r.top_result,
                    "execution_time": round(r.execution_time, 3),
                    "errors": r.errors
                }
                for r in results
            ]
        }
        
        # Save report
        with open("test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*60}")
        print("SEMANTIC SEARCH EVALUATION REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']} ({report['passed']/report['total_tests']:.1%})")
        print(f"Failed: {report['failed']} ({report['failed']/report['total_tests']:.1%})")
        print(f"Average Score: {report['average_score']:.3f}")
        print(f"Average Precision: {report['average_precision']:.3f}")
        print(f"Average Response Time: {report['average_execution_time']:.3f}s")
        
        print(f"\nFailed Tests:")
        for result in results:
            if not result.passed:
                print(f"  - '{result.query}': {', '.join(result.errors)}")

# Continuous benchmarking
class ContinuousBenchmark:
    """Run tests continuously and track performance over time"""
    
    def __init__(self):
        self.evaluator = RAGEvaluator()
        self.baseline_results = None
    
    async def run_benchmark(self):
        """Run benchmark and compare to baseline"""
        results = []
        for test_case in TEST_CASES:
            result = await self.evaluator.evaluate_single_query(test_case)
            results.append(result)
        
        current_score = sum(r.score for r in results) / len(results)
        
        if self.baseline_results is None:
            self.baseline_results = current_score
            print(f"Baseline established: {current_score:.3f}")
        else:
            improvement = current_score - self.baseline_results
            print(f"Current: {current_score:.3f} | Baseline: {self.baseline_results:.3f} | Change: {improvement:+.3f}")
            
            if improvement < -0.05:  # 5% degradation threshold
                print("⚠️  WARNING: Performance degradation detected!")
        
        return results

if __name__ == "__main__":
    # Run evaluation directly
    async def main():
        evaluator = RAGEvaluator()
        results = []
        
        print("Running semantic search evaluation...")
        for test_case in TEST_CASES:
            result = await evaluator.evaluate_single_query(test_case)
            results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} | {result.query[:40]:<40} | Score: {result.score:.3f} | Time: {result.execution_time:.3f}s")
        
        # Generate final report
        test_instance = TestSemanticSearch()
        test_instance._generate_report(results)
    
    # Run the evaluation
    asyncio.run(main())