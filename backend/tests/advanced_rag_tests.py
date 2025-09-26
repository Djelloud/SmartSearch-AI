"""
Advanced RAG testing with more sophisticated evaluation metrics
"""
import pytest
import asyncio
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import json
import logging
from datetime import datetime
from collections import defaultdict
import re
import sys
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
class AdvancedTestCase:
    query: str
    expected_categories: List[str]
    expected_keywords: List[str]
    expected_brands: List[str] = None
    price_range: Tuple[float, float] = None
    min_score_threshold: float = 0.3
    min_results: int = 1
    max_results: int = 10
    description: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    query_type: str = "general"  # direct, intent, semantic, complex

@dataclass
class AdvancedEvalResult:
    query: str
    passed: bool
    score: float
    precision_at_5: float
    recall_estimate: float
    category_accuracy: float
    keyword_coverage: float
    brand_accuracy: float
    price_relevance: float
    semantic_understanding: float
    results_count: int
    top_3_results: List[str]
    errors: List[str]
    execution_time: float
    difficulty: str
    query_type: str

class AdvancedRAGEvaluator:
    """Enhanced evaluation with more sophisticated metrics"""
    
    def __init__(self):
        self.search_service = SearchService()
        self.test_results = []
        
    async def evaluate_single_query(self, test_case: AdvancedTestCase) -> AdvancedEvalResult:
        """Enhanced evaluation with multiple quality metrics"""
        start_time = datetime.now()
        errors = []
        
        try:
            # Perform search
            results = await self.search_service.search(test_case.query, test_case.max_results)
            
            # Calculate multiple metrics
            precision_at_5 = self._calculate_precision_at_k(results, test_case, k=5)
            recall_estimate = self._estimate_recall(results, test_case)
            category_accuracy = self._calculate_category_accuracy(results, test_case)
            keyword_coverage = self._calculate_keyword_coverage(results, test_case)
            brand_accuracy = self._calculate_brand_accuracy(results, test_case)
            price_relevance = self._calculate_price_relevance(results, test_case)
            semantic_understanding = self._assess_semantic_understanding(results, test_case)
            
            avg_score = sum(r.score for r in results) / len(results) if results else 0
            
            # Enhanced pass/fail logic
            passed = self._determine_pass_status(
                results, test_case, precision_at_5, category_accuracy, 
                keyword_coverage, semantic_understanding
            )
            
            if not passed:
                errors = self._generate_failure_reasons(
                    results, test_case, precision_at_5, category_accuracy, 
                    keyword_coverage, semantic_understanding
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return AdvancedEvalResult(
                query=test_case.query,
                passed=passed,
                score=avg_score,
                precision_at_5=precision_at_5,
                recall_estimate=recall_estimate,
                category_accuracy=category_accuracy,
                keyword_coverage=keyword_coverage,
                brand_accuracy=brand_accuracy,
                price_relevance=price_relevance,
                semantic_understanding=semantic_understanding,
                results_count=len(results),
                top_3_results=[r.product.name for r in results[:3]],
                errors=errors,
                execution_time=execution_time,
                difficulty=test_case.difficulty,
                query_type=test_case.query_type
            )
            
        except Exception as e:
            return AdvancedEvalResult(
                query=test_case.query,
                passed=False,
                score=0.0,
                precision_at_5=0.0,
                recall_estimate=0.0,
                category_accuracy=0.0,
                keyword_coverage=0.0,
                brand_accuracy=0.0,
                price_relevance=0.0,
                semantic_understanding=0.0,
                results_count=0,
                top_3_results=[],
                errors=[str(e)],
                execution_time=(datetime.now() - start_time).total_seconds(),
                difficulty=test_case.difficulty,
                query_type=test_case.query_type
            )
    
    def _calculate_precision_at_k(self, results: List[SearchResult], test_case: AdvancedTestCase, k: int = 5) -> float:
        """Calculate precision@k with weighted relevance"""
        if not results:
            return 0.0
        
        relevant_count = 0
        for i, result in enumerate(results[:k]):
            relevance_score = self._calculate_relevance_score(result, test_case)
            # Weight by position (early results matter more)
            position_weight = 1.0 / (i + 1)
            relevant_count += relevance_score * position_weight
        
        # Normalize by maximum possible score
        max_possible = sum(1.0 / (i + 1) for i in range(min(k, len(results))))
        return relevant_count / max_possible if max_possible > 0 else 0.0
    
    def _estimate_recall(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Estimate recall based on expected categories and keywords"""
        if not results:
            return 0.0
        
        # This is a simplified recall estimation
        # In practice, you'd need a labeled dataset
        relevant_results = sum(
            1 for r in results if self._calculate_relevance_score(r, test_case) > 0.5
        )
        
        # Estimate total relevant items based on query complexity
        estimated_total_relevant = self._estimate_total_relevant(test_case)
        
        return min(relevant_results / estimated_total_relevant, 1.0)
    
    def _calculate_category_accuracy(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Calculate how well results match expected categories"""
        if not results or not test_case.expected_categories:
            return 1.0  # No category expectations
        
        category_matches = 0
        for result in results[:5]:  # Top 5
            result_category = result.product.category.lower()
            if any(expected.lower() in result_category or result_category in expected.lower() 
                   for expected in test_case.expected_categories):
                category_matches += 1
        
        return category_matches / min(5, len(results))
    
    def _calculate_keyword_coverage(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Calculate keyword coverage in top results"""
        if not results or not test_case.expected_keywords:
            return 1.0
        
        # Combine text from top 3 results
        combined_text = " ".join([
            f"{r.product.name} {r.product.description} {r.product.category}"
            for r in results[:3]
        ]).lower()
        
        matched_keywords = sum(
            1 for keyword in test_case.expected_keywords
            if keyword.lower() in combined_text
        )
        
        return matched_keywords / len(test_case.expected_keywords)
    
    def _calculate_brand_accuracy(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Calculate brand relevance if specified"""
        if not results or not test_case.expected_brands:
            return 1.0  # No brand expectations
        
        brand_matches = 0
        for result in results[:3]:
            result_brand = result.product.brand.lower()
            if any(expected.lower() in result_brand for expected in test_case.expected_brands):
                brand_matches += 1
        
        return brand_matches / min(3, len(results))
    
    def _calculate_price_relevance(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Calculate price range relevance"""
        if not results or not test_case.price_range:
            return 1.0  # No price expectations
        
        min_price, max_price = test_case.price_range
        relevant_count = 0
        
        for result in results[:5]:
            price = result.product.price
            # Allow some flexibility (±20%)
            flexible_min = min_price * 0.8
            flexible_max = max_price * 1.2
            
            if flexible_min <= price <= flexible_max:
                relevant_count += 1
            elif price <= max_price * 1.5:  # Partial credit for close prices
                relevant_count += 0.5
        
        return relevant_count / min(5, len(results))
    
    def _assess_semantic_understanding(self, results: List[SearchResult], test_case: AdvancedTestCase) -> float:
        """Assess how well the system understood semantic intent"""
        if not results:
            return 0.0
        
        # Analyze query intent patterns
        query_lower = test_case.query.lower()
        intent_signals = {
            'gift': ['gift', 'present', 'for'],
            'budget': ['budget', 'cheap', 'affordable', 'under'],
            'premium': ['premium', 'high-end', 'luxury', 'best'],
            'eco': ['eco', 'sustainable', 'organic', 'green'],
            'fitness': ['fitness', 'workout', 'exercise', 'gym'],
            'work': ['work', 'office', 'professional', 'business']
        }
        
        detected_intents = []
        for intent, signals in intent_signals.items():
            if any(signal in query_lower for signal in signals):
                detected_intents.append(intent)
        
        if not detected_intents:
            return 1.0  # No specific intent to evaluate
        
        # Check if results align with detected intents
        intent_alignment = 0
        for intent in detected_intents:
            alignment = self._check_intent_alignment(results, intent)
            intent_alignment += alignment
        
        return intent_alignment / len(detected_intents)
    
    def _check_intent_alignment(self, results: List[SearchResult], intent: str) -> float:
        """Check if results align with specific intent"""
        alignment_score = 0
        
        for result in results[:3]:
            product = result.product
            text = f"{product.name} {product.description} {product.category}".lower()
            
            if intent == 'gift':
                # Look for giftable items
                if any(word in text for word in ['gift', 'perfect', 'ideal', 'love']):
                    alignment_score += 1
            elif intent == 'budget':
                # Look for affordable options
                if product.price < 50 or any(word in text for word in ['budget', 'affordable', 'value']):
                    alignment_score += 1
            elif intent == 'premium':
                # Look for high-end items
                if product.price > 200 or any(word in text for word in ['premium', 'luxury', 'professional']):
                    alignment_score += 1
            elif intent == 'eco':
                # Look for eco-friendly items
                if any(word in text for word in ['eco', 'organic', 'sustainable', 'natural']):
                    alignment_score += 1
            elif intent == 'fitness':
                # Look for fitness-related items
                if any(word in text for word in ['fitness', 'sport', 'exercise', 'health']):
                    alignment_score += 1
            elif intent == 'work':
                # Look for work-related items
                if any(word in text for word in ['office', 'work', 'professional', 'business']):
                    alignment_score += 1
        
        return alignment_score / min(3, len(results))
    
    def _calculate_relevance_score(self, result: SearchResult, test_case: AdvancedTestCase) -> float:
        """Calculate overall relevance score for a single result"""
        scores = []
        
        # Category relevance
        if test_case.expected_categories:
            category_score = 1.0 if any(
                cat.lower() in result.product.category.lower() 
                for cat in test_case.expected_categories
            ) else 0.0
            scores.append(category_score)
        
        # Keyword relevance
        if test_case.expected_keywords:
            text = f"{result.product.name} {result.product.description}".lower()
            keyword_score = sum(
                1 for kw in test_case.expected_keywords 
                if kw.lower() in text
            ) / len(test_case.expected_keywords)
            scores.append(keyword_score)
        
        # Price relevance
        if test_case.price_range:
            min_price, max_price = test_case.price_range
            price = result.product.price
            if min_price <= price <= max_price:
                price_score = 1.0
            elif price <= max_price * 1.2:  # Within 20%
                price_score = 0.7
            else:
                price_score = 0.0
            scores.append(price_score)
        
        return sum(scores) / len(scores) if scores else result.score
    
    def _determine_pass_status(self, results, test_case, precision_at_5, category_accuracy, 
                              keyword_coverage, semantic_understanding) -> bool:
        """Enhanced pass/fail determination"""
        if len(results) < test_case.min_results:
            return False
        
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        
        # Adaptive thresholds based on difficulty
        score_threshold = {
            'easy': 0.6,
            'medium': 0.4,
            'hard': 0.3
        }.get(test_case.difficulty, 0.4)
        
        precision_threshold = {
            'easy': 0.8,
            'medium': 0.6,
            'hard': 0.4
        }.get(test_case.difficulty, 0.6)
        
        return (
            avg_score >= score_threshold and
            precision_at_5 >= precision_threshold and
            category_accuracy >= 0.4 and
            semantic_understanding >= 0.5
        )
    
    def _generate_failure_reasons(self, results, test_case, precision_at_5, 
                                 category_accuracy, keyword_coverage, semantic_understanding) -> List[str]:
        """Generate specific failure reasons"""
        errors = []
        
        if len(results) < test_case.min_results:
            errors.append(f"Insufficient results: {len(results)} < {test_case.min_results}")
        
        if precision_at_5 < 0.5:
            errors.append(f"Low precision@5: {precision_at_5:.3f}")
        
        if category_accuracy < 0.4:
            errors.append(f"Poor category matching: {category_accuracy:.3f}")
        
        if keyword_coverage < 0.3:
            errors.append(f"Low keyword coverage: {keyword_coverage:.3f}")
        
        if semantic_understanding < 0.5:
            errors.append(f"Poor semantic understanding: {semantic_understanding:.3f}")
        
        return errors
    
    def _estimate_total_relevant(self, test_case: AdvancedTestCase) -> int:
        """Estimate total relevant items for recall calculation"""
        # This is a heuristic - in practice you'd have labeled data
        base_estimate = 10
        
        if test_case.difficulty == 'easy':
            return base_estimate * 2
        elif test_case.difficulty == 'hard':
            return base_estimate // 2
        else:
            return base_estimate

# Enhanced test cases with more detailed specifications
ADVANCED_TEST_CASES = [
    AdvancedTestCase(
        query="wireless bluetooth headphones for running",
        expected_categories=["Electronics", "Sports"],
        expected_keywords=["wireless", "bluetooth", "headphone", "running", "sport"],
        price_range=(30.0, 200.0),
        min_score_threshold=0.6,
        difficulty="easy",
        query_type="direct",
        description="Direct product search with specific use case"
    ),
    
    AdvancedTestCase(
        query="thoughtful gift for someone who loves cooking",
        expected_categories=["Home & Garden", "Food & Beverage"],
        expected_keywords=["cooking", "kitchen", "chef", "culinary", "food"],
        min_score_threshold=0.4,
        difficulty="hard",
        query_type="intent",
        description="Intent-based gift recommendation requiring semantic understanding"
    ),
    
    AdvancedTestCase(
        query="eco-friendly sustainable products for environmentally conscious lifestyle",
        expected_categories=["Home & Garden", "Personal Care", "Food & Beverage"],
        expected_keywords=["eco", "sustainable", "organic", "natural", "environment"],
        min_score_threshold=0.4,
        difficulty="hard",
        query_type="semantic",
        description="Values-based search requiring deep semantic understanding"
    ),
    
    AdvancedTestCase(
        query="premium office chair for long coding sessions under 300 dollars",
        expected_categories=["Furniture"],
        expected_keywords=["chair", "office", "ergonomic", "coding", "desk"],
        price_range=(100.0, 300.0),
        min_score_threshold=0.5,
        difficulty="medium",
        query_type="complex",
        description="Complex query with specific use case and price constraint"
    ),
    
    AdvancedTestCase(
        query="compact fitness equipment for small apartment",
        expected_categories=["Sports", "Home & Garden"],
        expected_keywords=["fitness", "compact", "small", "apartment", "exercise"],
        min_score_threshold=0.4,
        difficulty="medium",
        query_type="semantic",
        description="Space-constrained fitness equipment search"
    )
]

class AdvancedTestSemanticSearch:
    """Advanced pytest test class with detailed metrics"""
    
    @pytest.fixture
    def evaluator(self):
        return AdvancedRAGEvaluator()
    
    @pytest.mark.asyncio
    async def test_advanced_evaluation(self, evaluator):
        """Run advanced evaluation with detailed metrics"""
        results = []
        
        for test_case in ADVANCED_TEST_CASES:
            result = await evaluator.evaluate_single_query(test_case)
            results.append(result)
        
        # Generate detailed report
        self._generate_advanced_report(results)
        
        # Assertions with context
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        avg_precision = sum(r.precision_at_5 for r in results) / len(results)
        avg_semantic = sum(r.semantic_understanding for r in results) / len(results)
        
        assert pass_rate >= 0.6, f"Pass rate too low: {pass_rate:.1%}"
        assert avg_precision >= 0.5, f"Average precision too low: {avg_precision:.3f}"
        assert avg_semantic >= 0.5, f"Semantic understanding too low: {avg_semantic:.3f}"
    
    def _generate_advanced_report(self, results: List[AdvancedEvalResult]):
        """Generate comprehensive advanced report"""
        
        # Group by difficulty and query type
        by_difficulty = defaultdict(list)
        by_query_type = defaultdict(list)
        
        for result in results:
            by_difficulty[result.difficulty].append(result)
            by_query_type[result.query_type].append(result)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "overall_metrics": {
                "pass_rate": sum(1 for r in results if r.passed) / len(results),
                "avg_precision_at_5": sum(r.precision_at_5 for r in results) / len(results),
                "avg_recall_estimate": sum(r.recall_estimate for r in results) / len(results),
                "avg_semantic_understanding": sum(r.semantic_understanding for r in results) / len(results),
                "avg_execution_time": sum(r.execution_time for r in results) / len(results)
            },
            "by_difficulty": {
                difficulty: {
                    "count": len(results_list),
                    "pass_rate": sum(1 for r in results_list if r.passed) / len(results_list),
                    "avg_precision": sum(r.precision_at_5 for r in results_list) / len(results_list)
                }
                for difficulty, results_list in by_difficulty.items()
            },
            "by_query_type": {
                query_type: {
                    "count": len(results_list),
                    "pass_rate": sum(1 for r in results_list if r.passed) / len(results_list),
                    "avg_semantic": sum(r.semantic_understanding for r in results_list) / len(results_list)
                }
                for query_type, results_list in by_query_type.items()
            },
            "detailed_results": [asdict(r) for r in results]
        }
        
        # Save detailed report
        with open("advanced_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*80}")
        print("ADVANCED SEMANTIC SEARCH EVALUATION")
        print(f"{'='*80}")
        
        print(f"\nOverall Metrics:")
        metrics = report["overall_metrics"]
        print(f"  Pass Rate: {metrics['pass_rate']:.1%}")
        print(f"  Precision@5: {metrics['avg_precision_at_5']:.3f}")
        print(f"  Recall (est.): {metrics['avg_recall_estimate']:.3f}")
        print(f"  Semantic Understanding: {metrics['avg_semantic_understanding']:.3f}")
        print(f"  Avg Response Time: {metrics['avg_execution_time']:.3f}s")
        
        print(f"\nBy Difficulty:")
        for difficulty, stats in report["by_difficulty"].items():
            print(f"  {difficulty.title()}: {stats['pass_rate']:.1%} pass rate, {stats['avg_precision']:.3f} precision")
        
        print(f"\nBy Query Type:")
        for query_type, stats in report["by_query_type"].items():
            print(f"  {query_type.title()}: {stats['pass_rate']:.1%} pass rate, {stats['avg_semantic']:.3f} semantic")
        
        print(f"\nFailed Tests:")
        failed_tests = [r for r in results if not r.passed]
        for result in failed_tests:
            print(f"  [{result.difficulty}/{result.query_type}] '{result.query}':")
            for error in result.errors:
                print(f"    - {error}")

if __name__ == "__main__":
    async def main():
        evaluator = AdvancedRAGEvaluator()
        results = []
        
        print("Running advanced semantic search evaluation...")
        for test_case in ADVANCED_TEST_CASES:
            result = await evaluator.evaluate_single_query(test_case)
            results.append(result)
            
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} | {result.query[:50]:<50} | P@5: {result.precision_at_5:.3f} | Semantic: {result.semantic_understanding:.3f}")
        
        # Generate final report
        test_instance = AdvancedTestSemanticSearch()
        test_instance._generate_advanced_report(results)
    
    asyncio.run(main())
