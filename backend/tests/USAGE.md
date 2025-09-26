# 🧪 How to Run the SmartSearch-AI Tests

## 🚀 Quick Start

### Step 1: Basic System Check
First, verify your system is working:

```bash
cd /home/amine/projects/SmartSearch-AI/backend
python test_basic.py
```

This will:
- ✅ Test if imports work
- ✅ Verify SearchService initialization  
- ✅ Run a basic search query
- ✅ Show sample results

### Step 2: Run Full Test Suite

Once basic test passes, run the comprehensive tests:

```bash
# Standard tests (recommended for daily development)
python run_tests.py

# Advanced tests with detailed metrics
python run_tests.py --advanced

# Production-level testing
python run_tests.py --environment production --advanced

# Continuous benchmarking
python run_tests.py --benchmark
```

## 📁 File Structure

```
backend/
├── run_tests.py           # ← Main test runner (use this!)
├── test_basic.py          # ← Basic system verification
└── tests/
    ├── test_runner.py     # Core test runner logic
    ├── rag_test_framework.py    # Standard RAG tests
    ├── advanced_rag_tests.py   # Advanced semantic tests
    ├── performance_tests.py    # Performance benchmarks
    ├── test_config.py          # Configuration & reporting
    └── README.md              # Detailed documentation
```

## 🎯 Different Test Modes

### 🟢 Development Mode (Default)
```bash
python run_tests.py
```
- **Pass Rate**: ≥60%
- **Precision**: ≥0.4
- **Max Response**: ≤2.0s
- **Use Case**: Daily development, quick feedback

### 🟡 Staging Mode
```bash
python run_tests.py --environment staging --advanced
```
- **Pass Rate**: ≥75%
- **Precision**: ≥0.6
- **Max Response**: ≤1.0s
- **Use Case**: Pre-release validation

### 🔴 Production Mode
```bash
python run_tests.py --environment production --advanced
```
- **Pass Rate**: ≥85%
- **Precision**: ≥0.7
- **Max Response**: ≤0.5s
- **Use Case**: Production readiness verification

## 📊 Understanding Test Results

### Standard Output
```
🧪 Starting SmartSearch-AI Evaluation Suite
Environment: DEVELOPMENT | Advanced: False
=====================================

📊 Running Standard Semantic Search Tests...
  ✅ wireless headphones: Score: 0.756 | Precision: 0.8
  ✅ gift for fitness enthusiast: Score: 0.423 | Precision: 0.6
  ❌ eco-friendly kitchen products: Score: 0.234 | Precision: 0.3

📋 COMPREHENSIVE EVALUATION SUMMARY
==================================
Accuracy Metrics:
  ✅ Passed: 7/8 (87.5%)
  📊 Average Score: 0.542
  🎯 Average Precision: 0.675

Performance Metrics:
  ⏱️  Response Time: 0.234s
  🔀 Concurrent Load: 0.456s
  💾 Memory Usage: +23.4MB

Overall Grade: A (Very Good)
```

### Generated Reports
After running tests, you'll find:
- `comprehensive_test_results.json` - Machine-readable results
- `test_report.html` - Beautiful web report (open in browser)
- `test_results.xml` - JUnit format for CI/CD
- `benchmarks.json` - Historical performance tracking

## 🔧 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'app.services'"

**Solution**: Always run from the backend directory:
```bash
cd /home/amine/projects/SmartSearch-AI/backend
python run_tests.py  # ← Correct
```

Don't run from the tests directory:
```bash
cd backend/tests
python test_runner.py  # ← Wrong (will fail)
```

### ❌ "Search failed" or "No results found"

**Possible causes**:
1. Database not running
2. No products in database
3. Embeddings not generated

**Solutions**:
```bash
# Check if database is running
docker-compose up postgres

# Initialize database and upload products
python scripts/init_db.py
python scripts/upload_products.py

# Verify search service works
python test_basic.py
```

### ❌ Import or dependency errors

**Solutions**:
```bash
# Install/update dependencies
pip install -r requirements.txt

# If using virtual environment
source venv/bin/activate  # or activate your venv
pip install -r requirements.txt
```

## 🎯 What Each Test Validates

### Standard Tests (`rag_test_framework.py`)
- **Direct searches**: "wireless headphones"
- **Intent searches**: "gift for fitness enthusiast"  
- **Lifestyle searches**: "work from home setup"
- **Budget searches**: "budget electronics under 100"
- **Values searches**: "eco-friendly kitchen products"

### Advanced Tests (`advanced_rag_tests.py`)
- **Semantic understanding**: Does AI understand user intent?
- **Precision@5**: Are top 5 results highly relevant?
- **Category accuracy**: Do results match expected categories?
- **Keyword coverage**: Are important keywords found in results?
- **Intent alignment**: Does the system understand gift/budget/eco intents?

### Performance Tests (`performance_tests.py`)
- **Response time**: Individual query speed
- **Concurrent load**: Performance under multiple users
- **Memory usage**: Resource consumption

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Semantic Search Tests
  run: |
    cd backend
    python run_tests.py --environment staging --advanced
    
- name: Check Quality Gates
  run: |
    if [ $? -ne 0 ]; then
      echo "Quality gates failed!"
      exit 1
    fi
```

### Quality Gates
The test runner returns:
- **Exit code 0**: All tests passed quality gates
- **Exit code 1**: Tests failed quality gates (fail the build)

## 📈 Monitoring & Benchmarking

### Track Performance Over Time
```bash
# Run this regularly to track trends
python run_tests.py --benchmark
```

### View Trends
- Check `benchmarks.json` for historical data
- Reports show 7-day trend analysis
- Automatic regression detection

## 💡 Best Practices

1. **Run basic test first**: `python test_basic.py`
2. **Daily development**: `python run_tests.py`
3. **Before releases**: `python run_tests.py --environment staging --advanced`
4. **Production monitoring**: Weekly production tests
5. **Track trends**: Regular benchmarking

---

## 🎉 Success Example

```bash
$ python run_tests.py --advanced

SmartSearch-AI Testing Suite v2.0
Environment: DEVELOPMENT
Advanced Mode: True

🔬 Running Advanced Semantic Search Tests...
  ✅ wireless bluetooth headphones for running: P@5: 0.856 | Semantic: 0.78
  ✅ thoughtful gift for someone who loves cooking: P@5: 0.672 | Semantic: 0.84
  ✅ eco-friendly sustainable products: P@5: 0.543 | Semantic: 0.71
  ✅ premium office chair for coding: P@5: 0.789 | Semantic: 0.66
  ✅ compact fitness equipment: P@5: 0.694 | Semantic: 0.72

⚡ Testing Performance...
  Response time: ✅ 0.234s (target: <2.0s)
  Concurrent load: ✅ 0.456s
  Memory usage: ✅ +18.2MB

📋 COMPREHENSIVE EVALUATION SUMMARY
Quality Gates: ✅ PASSED

Overall Grade: A+ (Excellent)

🎉 All quality gates passed for development environment!
📄 Reports generated:
  - test_report.html
  - comprehensive_test_results.json
  - test_results.xml

✅ Testing completed successfully!
```

That's it! Your semantic search is working excellently! 🚀
