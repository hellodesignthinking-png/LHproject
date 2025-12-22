# CI/CD Workflows Documentation

## ⚠️ Important Note

The following CI/CD workflow files were implemented but could not be pushed due to GitHub App permission restrictions (`workflows` permission required):

### 1. Premium Regression CI Blocking
**File**: `.github/workflows/ci-premium-regression.yml`

**Purpose**: Automatically test premium regression on every PR to ensure ±0.5% accuracy is maintained.

**Configuration**:
```yaml
name: Premium Regression CI Blocking

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  premium-regression-test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        cd /home/user/webapp
        python -m pip install --upgrade pip
        pip install -r requirements.txt || true
        
    - name: Run Premium Regression Test (CI BLOCKING)
      id: regression_test
      run: |
        cd /home/user/webapp
        python3 tests/test_appraisal_premium_regression.py
      continue-on-error: false
      
    - name: Verify Test Results
      run: |
        echo "✅ Premium Regression Test PASSED"
        echo "All premium rates and land values are within ±0.5% error margin"
        
    - name: Fail on Regression
      if: failure()
      run: |
        echo "❌ CRITICAL: Premium Regression Detected!"
        echo "PR cannot be merged until regression is fixed"
        echo "Error margin exceeded: ±0.5% threshold violated"
        exit 1
```

### 2. E2E Pipeline Immutability CI Blocking
**File**: `.github/workflows/ci-e2e-immutability.yml`

**Purpose**: Verify that appraisal immutability is maintained across all pipeline stages on every PR.

**Configuration**:
```yaml
name: E2E Pipeline Immutability CI Blocking

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  e2e-immutability-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        cd /home/user/webapp
        python -m pip install --upgrade pip
        pip install -r requirements.txt || true
        
    - name: Run E2E Pipeline Immutability Test (CI BLOCKING)
      id: e2e_test
      run: |
        cd /home/user/webapp
        python3 tests/test_e2e_pipeline_fixed.py
      continue-on-error: false
      
    - name: Verify Immutability
      run: |
        echo "✅ E2E Pipeline Immutability Test PASSED"
        echo "Appraisal Context remains LOCKED and READ-ONLY across all pipeline stages"
        echo "FACT → INTERPRETATION → JUDGMENT flow verified"
        
    - name: Fail on Immutability Violation
      if: failure()
      run: |
        echo "❌ CRITICAL: Pipeline Immutability Violation Detected!"
        echo "Appraisal context was modified after locking"
        echo "PR cannot be merged until immutability is guaranteed"
        exit 1
```

## 📋 Manual Setup Instructions

To enable these CI workflows, a repository administrator with `workflows` permission must:

1. **Copy the above YAML configurations** to the respective files in `.github/workflows/` directory
2. **Commit and push** the workflow files
3. **Enable GitHub Actions** in repository settings if not already enabled
4. **Configure branch protection rules** to require these checks to pass before merging

## ✅ Verification

Once enabled, these workflows will:
- Run automatically on every PR and push to `main` or `develop` branches
- Block merges if tests fail
- Provide clear feedback on what violations occurred
- Ensure data integrity and system reliability in production

## 🔒 Security Note

These CI checks are critical for maintaining:
- ±0.5% accuracy in appraisal calculations (preventing financial discrepancies)
- Immutable appraisal results (preventing tampering and disputes)
- Pipeline integrity (ensuring FACT → INTERPRETATION → JUDGMENT flow)

**DO NOT bypass these checks without proper review and approval.**
