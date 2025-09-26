"""
Test configuration and benchmarking utilities
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path

class TestConfig:
    """Configuration for different test environments"""
    
    ENVIRONMENTS = {
        "development": {
            "max_execution_time": 2.0,
            "min_pass_rate": 0.6,
            "min_precision": 0.4,
            "concurrent_users": 5,
            "test_iterations": 1
        },
        "staging": {
            "max_execution_time": 1.0,
            "min_pass_rate": 0.75,
            "min_precision": 0.6,
            "concurrent_users": 20,
            "test_iterations": 3
        },
        "production": {
            "max_execution_time": 0.5,
            "min_pass_rate": 0.85,
            "min_precision": 0.7,
            "concurrent_users": 50,
            "test_iterations": 5
        }
    }
    
    @classmethod
    def get_config(cls, environment: str = "development") -> Dict[str, Any]:
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS["development"])

class BenchmarkTracker:
    """Track performance over time"""
    
    def __init__(self, benchmark_file: str = "benchmarks.json"):
        self.benchmark_file = Path(benchmark_file)
        self.benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self) -> List[Dict[str, Any]]:
        if self.benchmark_file.exists():
            with open(self.benchmark_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_benchmark(self, results: Dict[str, Any]):
        """Save benchmark results"""
        benchmark_entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": results,
            "git_commit": self._get_git_commit(),
            "environment": results.get("environment", "unknown")
        }
        
        self.benchmarks.append(benchmark_entry)
        
        # Keep only last 100 benchmarks
        self.benchmarks = self.benchmarks[-100:]
        
        with open(self.benchmark_file, 'w') as f:
            json.dump(self.benchmarks, f, indent=2)
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()[:8]  # Short hash
        except:
            return "unknown"
    
    def get_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_benchmarks = [
            b for b in self.benchmarks 
            if datetime.fromisoformat(b["timestamp"]) > cutoff_date
        ]
        
        if len(recent_benchmarks) < 2:
            return {"status": "insufficient_data", "count": len(recent_benchmarks)}
        
        # Calculate trends
        pass_rates = [b["metrics"].get("pass_rate", 0) for b in recent_benchmarks]
        avg_scores = [b["metrics"].get("avg_score", 0) for b in recent_benchmarks]
        response_times = [b["metrics"].get("avg_response_time", 0) for b in recent_benchmarks]
        
        return {
            "status": "analyzed",
            "count": len(recent_benchmarks),
            "trends": {
                "pass_rate": {
                    "current": pass_rates[-1] if pass_rates else 0,
                    "average": sum(pass_rates) / len(pass_rates) if pass_rates else 0,
                    "trend": "improving" if len(pass_rates) > 1 and pass_rates[-1] > pass_rates[0] else "declining"
                },
                "avg_score": {
                    "current": avg_scores[-1] if avg_scores else 0,
                    "average": sum(avg_scores) / len(avg_scores) if avg_scores else 0,
                    "trend": "improving" if len(avg_scores) > 1 and avg_scores[-1] > avg_scores[0] else "declining"
                },
                "response_time": {
                    "current": response_times[-1] if response_times else 0,
                    "average": sum(response_times) / len(response_times) if response_times else 0,
                    "trend": "improving" if len(response_times) > 1 and response_times[-1] < response_times[0] else "declining"
                }
            }
        }
    
    def detect_regressions(self, current_results: Dict[str, Any], threshold: float = 0.1) -> List[str]:
        """Detect performance regressions"""
        if len(self.benchmarks) < 3:
            return []
        
        # Get baseline from last 3 runs (excluding current)
        recent = self.benchmarks[-3:]
        baseline_pass_rate = sum(b["metrics"].get("pass_rate", 0) for b in recent) / len(recent)
        baseline_score = sum(b["metrics"].get("avg_score", 0) for b in recent) / len(recent)
        baseline_time = sum(b["metrics"].get("avg_response_time", 999) for b in recent) / len(recent)
        
        regressions = []
        
        # Check for regressions
        current_pass_rate = current_results.get("pass_rate", 0)
        current_score = current_results.get("avg_score", 0)
        current_time = current_results.get("avg_response_time", 999)
        
        if current_pass_rate < baseline_pass_rate - threshold:
            regressions.append(f"Pass rate regression: {current_pass_rate:.1%} vs {baseline_pass_rate:.1%}")
        
        if current_score < baseline_score - threshold:
            regressions.append(f"Score regression: {current_score:.3f} vs {baseline_score:.3f}")
        
        if current_time > baseline_time * (1 + threshold):
            regressions.append(f"Performance regression: {current_time:.3f}s vs {baseline_time:.3f}s")
        
        return regressions

class TestReportGenerator:
    """Generate comprehensive test reports"""
    
    @staticmethod
    def generate_html_report(results: Dict[str, Any], output_file: str = "test_report.html"):
        """Generate HTML test report"""
        
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>SmartSearch-AI Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #4CAF50; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .test-results {{ margin-top: 30px; }}
        .test-item {{ background: #fff; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .test-item.passed {{ border-left: 4px solid #4CAF50; }}
        .test-item.failed {{ border-left: 4px solid #f44336; }}
        .query {{ font-weight: bold; color: #333; }}
        .details {{ margin-top: 10px; color: #666; font-size: 0.9em; }}
        .error {{ color: #f44336; background: #ffebee; padding: 5px; border-radius: 3px; margin: 5px 0; }}
        .timestamp {{ text-align: center; color: #999; margin-top: 30px; }}
        .grade {{ font-size: 3em; color: #4CAF50; text-align: center; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SmartSearch-AI Test Report</h1>
            <p>Comprehensive evaluation of semantic search performance</p>
        </div>
        
        <div class="grade">Grade: {grade}</div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{pass_rate}</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_score:.3f}</div>
                <div class="metric-label">Average Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_precision:.3f}</div>
                <div class="metric-label">Average Precision</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_time:.3f}s</div>
                <div class="metric-label">Response Time</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>Test Results</h2>
            {test_items}
        </div>
        
        <div class="timestamp">
            Generated on {timestamp}
        </div>
    </div>
</body>
</html>"""
        
        # Generate test items HTML
        test_items_html = ""
        for result in results.get("results", []):
            status_class = "passed" if result.get("passed", False) else "failed"
            status_icon = "✅" if result.get("passed", False) else "❌"
            
            errors_html = ""
            if result.get("errors"):
                errors_html = "".join([f'<div class="error">{error}</div>' for error in result["errors"]])
            
            test_items_html += f"""
            <div class="test-item {status_class}">
                <div class="query">{status_icon} {result.get('query', 'Unknown')}</div>
                <div class="details">
                    Score: {result.get('score', 0):.3f} | 
                    Precision: {result.get('precision', 0):.3f} | 
                    Time: {result.get('execution_time', 0):.3f}s
                    {f"<br>Top Result: {result.get('top_result', 'N/A')}" if result.get('top_result') else ""}
                </div>
                {errors_html}
            </div>
            """
        
        # Calculate metrics
        total_tests = results.get("total_tests", 0)
        passed_tests = results.get("passed", 0)
        pass_rate = f"{passed_tests}/{total_tests} ({passed_tests/total_tests:.1%})" if total_tests > 0 else "0/0 (0%)"
        
        # Populate template
        html_content = html_template.format(
            grade=results.get("grade", "Unknown"),
            pass_rate=pass_rate,
            avg_score=results.get("average_score", 0),
            avg_precision=results.get("average_precision", 0),
            avg_time=results.get("average_execution_time", 0),
            test_items=test_items_html,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Write HTML file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 HTML report generated: {output_file}")

class ContinuousIntegrationHelper:
    """Helper for CI/CD integration"""
    
    @staticmethod
    def generate_junit_xml(results: Dict[str, Any], output_file: str = "test_results.xml"):
        """Generate JUnit XML for CI systems"""
        
        xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="SemanticSearchTests" tests="{total_tests}" failures="{failures}" time="{total_time}">
        {test_cases}
    </testsuite>
</testsuites>"""
        
        test_cases_xml = ""
        for result in results.get("results", []):
            passed = result.get("passed", False)
            test_name = result.get("query", "unknown").replace('"', '&quot;')
            execution_time = result.get("execution_time", 0)
            
            if passed:
                test_cases_xml += f'<testcase name="{test_name}" time="{execution_time:.3f}"/>\n        '
            else:
                errors = " | ".join(result.get("errors", []))
                test_cases_xml += f"""<testcase name="{test_name}" time="{execution_time:.3f}">
            <failure message="Test failed">{errors}</failure>
        </testcase>
        """
        
        total_tests = results.get("total_tests", 0)
        failures = results.get("failed", 0)
        total_time = results.get("average_execution_time", 0) * total_tests
        
        xml_content = xml_template.format(
            total_tests=total_tests,
            failures=failures,
            total_time=total_time,
            test_cases=test_cases_xml
        )
        
        with open(output_file, 'w') as f:
            f.write(xml_content)
        
        print(f"📊 JUnit XML generated: {output_file}")
    
    @staticmethod
    def check_quality_gates(results: Dict[str, Any], environment: str = "development") -> bool:
        """Check if results meet quality gates"""
        config = TestConfig.get_config(environment)
        
        pass_rate = results.get("passed", 0) / results.get("total_tests", 1)
        avg_precision = results.get("average_precision", 0)
        avg_time = results.get("average_execution_time", 0)
        
        gates_passed = []
        gates_passed.append(pass_rate >= config["min_pass_rate"])
        gates_passed.append(avg_precision >= config["min_precision"])
        gates_passed.append(avg_time <= config["max_execution_time"])
        
        return all(gates_passed)
