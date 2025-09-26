#!/usr/bin/env python3
"""
Automated testing suite for SmartSearch-AI semantic search
Run this to evaluate your RAG system comprehensively
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
# Also add the backend/tests directory for relative imports
tests_path = Path(__file__).parent
sys.path.insert(0, str(tests_path))

try:
    from rag_test_framework import RAGEvaluator, TEST_CASES
    from performance_tests import PerformanceTestSuite
    from advanced_rag_tests import AdvancedRAGEvaluator, ADVANCED_TEST_CASES
    from test_config import TestConfig, BenchmarkTracker, TestReportGenerator, ContinuousIntegrationHelper
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the backend directory or the backend/tests directory")
    sys.exit(1)

class TestRunner:
    """Enhanced test runner with advanced features"""
    
    def __init__(self, environment: str = "development", advanced: bool = False):
        self.environment = environment
        self.config = TestConfig.get_config(environment)
        self.rag_evaluator = RAGEvaluator()
        self.advanced_evaluator = AdvancedRAGEvaluator() if advanced else None
        self.perf_suite = PerformanceTestSuite()
        self.benchmark_tracker = BenchmarkTracker()
        self.advanced_mode = advanced
    
    async def run_full_evaluation(self):
        """Enhanced evaluation with advanced features"""
        print(f"🧪 Starting SmartSearch-AI Evaluation Suite")
        print(f"Environment: {self.environment.upper()} | Advanced: {self.advanced_mode}")
        print("=" * 70)
        
        # 1. Choose test suite
        if self.advanced_mode:
            print("\n🔬 Running Advanced Semantic Search Tests...")
            evaluator = self.advanced_evaluator
            test_cases = ADVANCED_TEST_CASES
        else:
            print("\n📊 Running Standard Semantic Search Tests...")
            evaluator = self.rag_evaluator
            test_cases = TEST_CASES
        
        # Run accuracy tests
        accuracy_results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"  {i}/{len(test_cases)}: {test_case.query[:50]}")
            result = await evaluator.evaluate_single_query(test_case)
            accuracy_results.append(result)
            
            status = "✅" if result.passed else "❌"
            if self.advanced_mode:
                print(f"    {status} P@5: {result.precision_at_5:.3f} | Semantic: {result.semantic_understanding:.3f}")
            else:
                print(f"    {status} Score: {result.score:.3f} | Precision: {result.precision:.3f}")
        
        # 2. Performance Tests
        print(f"\n⚡ Testing Performance (Environment: {self.environment})...")
        try:
            response_times = await self.perf_suite.test_response_time()
            concurrent_times = await self.perf_suite.test_concurrent_load()
            memory_usage = await self.perf_suite.test_memory_usage()
        except Exception as e:
            print(f"Performance test failed: {e}")
            response_times = concurrent_times = [999]
            memory_usage = 999
        
        # 3. Generate comprehensive results
        results = self._compile_results(accuracy_results, response_times, concurrent_times, memory_usage)
        
        # 4. Check for regressions
        regressions = self.benchmark_tracker.detect_regressions(results)
        if regressions:
            print(f"\n⚠️  REGRESSIONS DETECTED:")
            for regression in regressions:
                print(f"  - {regression}")
        
        # 5. Save benchmark
        self.benchmark_tracker.save_benchmark(results)
        
        # 6. Generate reports
        self._generate_all_reports(results)
        
        # 7. Check quality gates
        gates_passed = ContinuousIntegrationHelper.check_quality_gates(results, self.environment)
        
        # 8. Print summary
        self._print_enhanced_summary(results, gates_passed)
        
        return accuracy_results, gates_passed
    
    def _print_summary(self, accuracy_results, response_times, concurrent_times, memory_usage):
        """Print comprehensive test summary"""
        print(f"\n📋 EVALUATION SUMMARY")
        print("=" * 60)
        
        # Accuracy metrics
        passed_tests = sum(1 for r in accuracy_results if r.passed)
        total_tests = len(accuracy_results)
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        avg_score = sum(r.score for r in accuracy_results) / total_tests if total_tests > 0 else 0
        avg_precision = sum(r.precision for r in accuracy_results) / total_tests if total_tests > 0 else 0
        
        # Performance metrics
        avg_response = sum(response_times) / len(response_times) if response_times else 999
        avg_concurrent = sum(concurrent_times) / len(concurrent_times) if concurrent_times else 999
        
        print(f"Accuracy Tests:")
        print(f"  ✅ Passed: {passed_tests}/{total_tests} ({pass_rate:.1%})")
        print(f"  📊 Average Score: {avg_score:.3f}")
        print(f"  🎯 Average Precision: {avg_precision:.3f}")
        
        print(f"\nPerformance Tests:")
        print(f"  ⏱️  Avg Response Time: {avg_response:.3f}s")
        print(f"  🔀 Concurrent Performance: {avg_concurrent:.3f}s")
        print(f"  💾 Memory Usage: +{memory_usage:.1f}MB")
        
        # Overall grade
        grade = self._calculate_grade(pass_rate, avg_score, avg_response)
        print(f"\nOverall Grade: {grade}")
        
        # Recommendations
        self._print_recommendations(accuracy_results, avg_response, avg_precision)
    
    def _calculate_grade(self, pass_rate, avg_score, avg_response):
        """Calculate overall system grade"""
        score = 0
        
        # Accuracy component (60% weight)
        if pass_rate >= 0.9: score += 60
        elif pass_rate >= 0.8: score += 50
        elif pass_rate >= 0.7: score += 40
        elif pass_rate >= 0.6: score += 30
        else: score += int(pass_rate * 30)
        
        # Quality component (25% weight)
        if avg_score >= 0.7: score += 25
        elif avg_score >= 0.6: score += 20
        elif avg_score >= 0.5: score += 15
        elif avg_score >= 0.4: score += 10
        else: score += int(avg_score * 10)
        
        # Performance component (15% weight)
        if avg_response <= 0.2: score += 15
        elif avg_response <= 0.5: score += 12
        elif avg_response <= 1.0: score += 8
        elif avg_response <= 2.0: score += 5
        else: score += 2
        
        if score >= 90: return "A+ (Excellent)"
        elif score >= 85: return "A (Very Good)"
        elif score >= 80: return "B+ (Good)"
        elif score >= 75: return "B (Satisfactory)"
        elif score >= 70: return "C+ (Needs Improvement)"
        else: return "C (Major Issues)"
    
    def _print_recommendations(self, results, avg_response, avg_precision):
        """Print improvement recommendations"""
        print(f"\n💡 RECOMMENDATIONS:")
        
        # Check for common failure patterns
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            print(f"  • {len(failed_results)} tests failed - consider:")
            for result in failed_results[:3]:  # Show top 3 failures
                print(f"    - '{result.query}': {', '.join(result.errors)}")
        
        if avg_precision < 0.6:
            print(f"  • Low precision ({avg_precision:.2f}) - improve product descriptions")
        
        if avg_response > 0.5:
            print(f"  • Slow responses ({avg_response:.2f}s) - consider caching or optimization")
        
        # Check for category gaps
        category_performance = {}
        for result in results:
            # This is simplified - you'd need to map queries to categories
            if "fitness" in result.query.lower():
                category_performance.setdefault("fitness", []).append(result.score)
        
        for category, scores in category_performance.items():
            avg_cat_score = sum(scores) / len(scores)
            if avg_cat_score < 0.4:
                print(f"  • Weak performance in {category} queries - add more diverse products")
        
        if all(r.passed for r in results):
            print(f"  🎉 All tests passed! Your semantic search is working well.")
            print(f"  📈 Consider adding more complex test cases for edge cases.")
    
    def _compile_results(self, accuracy_results, response_times, concurrent_times, memory_usage):
        """Compile comprehensive results"""
        passed_tests = sum(1 for r in accuracy_results if r.passed)
        total_tests = len(accuracy_results)
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        if self.advanced_mode:
            avg_score = sum(r.score for r in accuracy_results) / total_tests if total_tests > 0 else 0
            avg_precision = sum(r.precision_at_5 for r in accuracy_results) / total_tests if total_tests > 0 else 0
            avg_semantic = sum(r.semantic_understanding for r in accuracy_results) / total_tests if total_tests > 0 else 0
        else:
            avg_score = sum(r.score for r in accuracy_results) / total_tests if total_tests > 0 else 0
            avg_precision = sum(r.precision for r in accuracy_results) / total_tests if total_tests > 0 else 0
            avg_semantic = 0.0
        
        avg_response = sum(response_times) / len(response_times) if response_times else 999
        avg_concurrent = sum(concurrent_times) / len(concurrent_times) if concurrent_times else 999
        
        grade = self._calculate_grade(pass_rate, avg_score, avg_response)
        
        return {
            "environment": self.environment,
            "advanced_mode": self.advanced_mode,
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": pass_rate,
            "average_score": avg_score,
            "average_precision": avg_precision,
            "average_semantic_understanding": avg_semantic,
            "average_execution_time": sum(r.execution_time for r in accuracy_results) / total_tests if total_tests > 0 else 0,
            "avg_response_time": avg_response,
            "avg_concurrent_time": avg_concurrent,
            "memory_usage": memory_usage,
            "grade": grade,
            "results": [
                {
                    "query": r.query,
                    "passed": r.passed,
                    "score": r.score,
                    "precision": getattr(r, 'precision_at_5', getattr(r, 'precision', 0)),
                    "top_result": getattr(r, 'top_3_results', [r.top_result])[0] if hasattr(r, 'top_3_results') and r.top_3_results else r.top_result,
                    "execution_time": r.execution_time,
                    "errors": r.errors
                }
                for r in accuracy_results
            ]
        }
    
    def _generate_all_reports(self, results):
        """Generate all report formats"""
        # JSON report
        import json
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # HTML report
        TestReportGenerator.generate_html_report(results, "test_report.html")
        
        # JUnit XML for CI
        ContinuousIntegrationHelper.generate_junit_xml(results, "test_results.xml")
        
        print(f"📄 Reports generated:")
        print(f"  - comprehensive_test_results.json")
        print(f"  - test_report.html")
        print(f"  - test_results.xml")
    
    def _print_enhanced_summary(self, results, gates_passed):
        """Print enhanced summary with quality gates"""
        print(f"\n📋 COMPREHENSIVE EVALUATION SUMMARY")
        print("=" * 70)
        
        print(f"Environment: {results['environment'].upper()}")
        print(f"Mode: {'Advanced' if results['advanced_mode'] else 'Standard'}")
        print(f"Quality Gates: {'✅ PASSED' if gates_passed else '❌ FAILED'}")
        
        print(f"\nAccuracy Metrics:")
        print(f"  ✅ Passed: {results['passed']}/{results['total_tests']} ({results['pass_rate']:.1%})")
        print(f"  📊 Average Score: {results['average_score']:.3f}")
        print(f"  🎯 Average Precision: {results['average_precision']:.3f}")
        if results['advanced_mode']:
            print(f"  🧠 Semantic Understanding: {results['average_semantic_understanding']:.3f}")
        
        print(f"\nPerformance Metrics:")
        print(f"  ⏱️  Response Time: {results['avg_response_time']:.3f}s")
        print(f"  🔀 Concurrent Load: {results['avg_concurrent_time']:.3f}s")
        print(f"  💾 Memory Usage: +{results['memory_usage']:.1f}MB")
        
        print(f"\nOverall Grade: {results['grade']}")
        
        # Show trend analysis
        trend_analysis = self.benchmark_tracker.get_trend_analysis()
        if trend_analysis["status"] == "analyzed":
            print(f"\n📈 Trend Analysis (Last 7 days):")
            trends = trend_analysis["trends"]
            print(f"  Pass Rate: {trends['pass_rate']['trend']}")
            print(f"  Score: {trends['avg_score']['trend']}")
            print(f"  Performance: {trends['response_time']['trend']}")
        
        # Environment-specific recommendations
        config = self.config
        print(f"\n💡 RECOMMENDATIONS FOR {self.environment.upper()}:")
        if results['pass_rate'] < config['min_pass_rate']:
            print(f"  ⚠️  Pass rate below threshold ({results['pass_rate']:.1%} < {config['min_pass_rate']:.1%})")
        if results['average_precision'] < config['min_precision']:
            print(f"  ⚠️  Precision below threshold ({results['average_precision']:.3f} < {config['min_precision']:.3f})")
        if results['avg_response_time'] > config['max_execution_time']:
            print(f"  ⚠️  Response time above threshold ({results['avg_response_time']:.3f}s > {config['max_execution_time']:.3f}s)")
        
        if gates_passed:
            print(f"  🎉 All quality gates passed for {self.environment} environment!")

async def main():
    """Enhanced main function with argument parsing"""
    parser = argparse.ArgumentParser(description="SmartSearch-AI Testing Suite")
    parser.add_argument("--environment", "-e", choices=["development", "staging", "production"], 
                       default="development", help="Test environment")
    parser.add_argument("--advanced", "-a", action="store_true", 
                       help="Run advanced tests with detailed metrics")
    parser.add_argument("--benchmark", "-b", action="store_true", 
                       help="Run continuous benchmarking")
    
    args = parser.parse_args()
    
    runner = TestRunner(environment=args.environment, advanced=args.advanced)
    
    print(f"SmartSearch-AI Testing Suite v2.0")
    print(f"Environment: {args.environment.upper()}")
    print(f"Advanced Mode: {args.advanced}")
    print("This will evaluate your semantic search accuracy and performance\n")
    
    try:
        if args.benchmark:
            # Run continuous benchmarking
            from rag_test_framework import ContinuousBenchmark
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

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)