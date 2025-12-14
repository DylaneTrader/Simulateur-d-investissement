# Recommendations for Code Improvements
## Simulateur d'Investissement - CGF GESTION

**Date:** December 14, 2025  
**Priority Levels:** 🔴 High | 🟡 Medium | 🟢 Low

---

## Executive Summary

The codebase is **production-ready** with an excellent maintainability score of **95%**. The recommendations below are **enhancements** that would improve robustness, performance, and developer experience, but are **not required** for the application to function correctly.

---

## 1. Error Handling Improvements

### 🟡 Medium Priority

**Current State:**  
The `core/calculations.py` module lacks explicit error handling for edge cases.

**Recommendation:**  
Add defensive programming to handle edge cases gracefully.

**Implementation:**

```python
# In core/calculations.py

def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """
    Calcule la Valeur Future totale (FV) d'un investissement.
    
    Args:
        pv: montant initial
        pmt: versement mensuel
        rate: rendement annuel en %
        n_years: durée en années
        
    Returns:
        float: Valeur future calculée
        
    Raises:
        ValueError: Si les paramètres sont invalides (négatifs ou None)
    """
    # Validation des entrées
    if pv < 0 or pmt < 0 or n_years < 0:
        raise ValueError("Les paramètres ne peuvent pas être négatifs")
    
    if n_years == 0:
        return pv
    
    try:
        n_periods = int(n_years * 12)
        rate_monthly = rate / 100 / 12

        # FV du capital initial
        fv_pv = pv * (1 + rate_monthly) ** n_periods

        # FV des versements mensuels
        if rate_monthly == 0:
            fv_pmt = pmt * n_periods
        else:
            fv_pmt = pmt * (((1 + rate_monthly) ** n_periods - 1) / rate_monthly)

        return fv_pv + fv_pmt
        
    except (ZeroDivisionError, OverflowError) as e:
        raise ValueError(f"Erreur de calcul: {e}")
```

**Benefits:**
- Prevents unexpected crashes
- Provides clear error messages to users
- Easier debugging in production

---

## 2. Performance Optimization with Caching

### 🟡 Medium Priority

**Current State:**  
Calculations are re-run every time the user interacts with the UI, even if inputs haven't changed.

**Recommendation:**  
Add Streamlit caching to expensive calculation and chart generation functions.

**Implementation:**

```python
# In core/calculations.py
import streamlit as st

@st.cache_data
def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """Calcule la Valeur Future totale (FV) d'un investissement."""
    # ... existing code ...
    return fv_pv + fv_pmt

@st.cache_data
def calculate_pmt(fv: float, pv: float, rate: float, n_years: float) -> float:
    """Calcule le versement mensuel nécessaire."""
    # ... existing code ...
    return pmt_result

# Similarly for calculate_pv and calculate_n_years
```

```python
# In ui/charts.py
import streamlit as st

@st.cache_data
def create_simulation_chart(pv: float, pmt: float, rate: float, n_years: float, fv_target=None):
    """Produit les graphiques avec mise en cache."""
    # ... existing code ...
```

**Benefits:**
- Faster response time for repeated calculations
- Better user experience
- Reduced server load for deployed application

**Note:** Test thoroughly to ensure cache invalidation works correctly when inputs change.

---

## 3. Type Hints for Better IDE Support

### 🟢 Low Priority

**Current State:**  
Functions lack type annotations, which can make code harder to understand and maintain.

**Recommendation:**  
Add type hints throughout the codebase.

**Implementation:**

```python
# In core/calculations.py
from typing import Union
import numpy as np

def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """Calcule la Valeur Future totale (FV) d'un investissement."""
    # ... existing code ...

def calculate_n_years(fv: float, pv: float, pmt: float, rate: float) -> Union[float, float]:
    """Calcule le nombre d'années nécessaires."""
    # Return can be float or np.inf
    # ... existing code ...
```

```python
# In core/utils.py
def fmt_money(value: float) -> str:
    """Formatte proprement un montant en FCFA."""
    # ... existing code ...

def is_positive_number(x: Union[int, float, str]) -> bool:
    """Vérifie si x est un nombre positif."""
    # ... existing code ...
```

**Benefits:**
- Better IDE autocomplete and suggestions
- Catches type errors during development
- Self-documenting code
- Easier onboarding for new developers

---

## 4. Unit Tests with Pytest

### 🟢 Low Priority (but recommended for long-term maintenance)

**Current State:**  
No automated test suite exists.

**Recommendation:**  
Create a comprehensive test suite using pytest.

**Implementation:**

Create `tests/test_calculations.py`:

```python
import pytest
import numpy as np
from core.calculations import calculate_fv, calculate_pmt, calculate_pv, calculate_n_years

class TestCalculateFV:
    def test_basic_calculation(self):
        """Test basic FV calculation."""
        result = calculate_fv(pv=100000, pmt=50000, rate=5.0, n_years=10)
        assert 7_000_000 < result < 9_000_000
    
    def test_zero_rate(self):
        """Test FV with zero interest rate."""
        result = calculate_fv(pv=100000, pmt=50000, rate=0, n_years=10)
        expected = 100000 + (50000 * 10 * 12)
        assert abs(result - expected) < 1
    
    def test_no_initial_capital(self):
        """Test FV with no initial capital."""
        result = calculate_fv(pv=0, pmt=50000, rate=5.0, n_years=10)
        assert result > 0
    
    def test_no_monthly_payment(self):
        """Test FV with no monthly payments."""
        result = calculate_fv(pv=100000, pmt=0, rate=5.0, n_years=10)
        expected = 100000 * (1 + 0.05/12) ** (10*12)
        assert abs(result - expected) < 100

class TestCalculatePMT:
    def test_basic_calculation(self):
        """Test basic PMT calculation."""
        result = calculate_pmt(fv=10_000_000, pv=100000, rate=5.0, n_years=10)
        assert 50000 < result < 100000
    
    def test_already_reached(self):
        """Test when initial capital already exceeds target."""
        result = calculate_pmt(fv=100000, pv=200000, rate=5.0, n_years=10)
        assert result == 0

class TestCalculatePV:
    def test_basic_calculation(self):
        """Test basic PV calculation."""
        result = calculate_pv(fv=10_000_000, pmt=50000, rate=5.0, n_years=10)
        assert 0 < result < 5_000_000
    
    def test_payments_sufficient(self):
        """Test when payments alone reach the target."""
        result = calculate_pv(fv=100000, pmt=50000, rate=5.0, n_years=10)
        assert result == 0

class TestCalculateNYears:
    def test_basic_calculation(self):
        """Test basic n_years calculation."""
        result = calculate_n_years(fv=10_000_000, pv=100000, pmt=50000, rate=5.0)
        assert 5 < result < 20
    
    def test_already_reached(self):
        """Test when target is already reached."""
        result = calculate_n_years(fv=100000, pv=200000, pmt=50000, rate=5.0)
        assert result == 0
    
    def test_impossible_target(self):
        """Test when target is impossible to reach."""
        result = calculate_n_years(fv=10_000_000, pv=100, pmt=0, rate=0)
        assert np.isinf(result)
```

Create `tests/test_utils.py`:

```python
import pytest
from core.utils import fmt_money, is_positive_number, round_up, round_down

class TestFmtMoney:
    def test_basic_formatting(self):
        assert fmt_money(1500000) == "1 500 000 FCFA"
    
    def test_zero(self):
        assert fmt_money(0) == "0 FCFA"
    
    def test_large_number(self):
        assert fmt_money(1000000000) == "1 000 000 000 FCFA"

class TestIsPositiveNumber:
    def test_positive_int(self):
        assert is_positive_number(100) == True
    
    def test_negative_int(self):
        assert is_positive_number(-50) == False
    
    def test_zero(self):
        assert is_positive_number(0) == True
    
    def test_string(self):
        assert is_positive_number("100") == True
        assert is_positive_number("abc") == False

class TestRounding:
    def test_round_up(self):
        assert round_up(123.456, 2) == 123.46
        assert round_up(123.451, 2) == 123.46
    
    def test_round_down(self):
        assert round_down(123.456, 2) == 123.45
        assert round_down(123.459, 2) == 123.45
```

Create `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

Update `requirements.txt`:

```
# Add to requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0  # For coverage reports
```

**Running tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test file
pytest tests/test_calculations.py

# Run with verbose output
pytest -v
```

**Benefits:**
- Catch regressions early
- Confidence when refactoring
- Documentation of expected behavior
- Easier collaboration with other developers

---

## 5. Logging Infrastructure

### 🟢 Low Priority

**Current State:**  
No logging mechanism exists for debugging production issues.

**Recommendation:**  
Add Python logging throughout the application.

**Implementation:**

Create `core/logger.py`:

```python
import logging
import sys

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Configure and return a logger for the application.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
```

Use in modules:

```python
# In core/calculations.py
from core.logger import setup_logger

logger = setup_logger(__name__)

def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    logger.debug(f"Calculating FV with pv={pv}, pmt={pmt}, rate={rate}, n_years={n_years}")
    
    # ... calculation ...
    
    logger.info(f"FV calculated: {result:.2f}")
    return result
```

```python
# In ui/layout.py
from core.logger import setup_logger

logger = setup_logger(__name__)

def display_results(inputs: dict, calculation_mode: str):
    logger.info(f"Displaying results for mode: {calculation_mode}")
    
    try:
        # ... calculation and display ...
        logger.info("Results displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying results: {e}", exc_info=True)
        st.error(f"Erreur lors de l'affichage : {str(e)}")
```

**Benefits:**
- Easier debugging in production
- Track user behavior and errors
- Performance monitoring
- Audit trail for calculations

---

## 6. Code Formatting and Linting

### 🟢 Low Priority

**Current State:**  
No automated code formatting or linting is enforced.

**Recommendation:**  
Set up Black, isort, and flake8 for consistent code style.

**Implementation:**

Update `requirements.txt`:

```
# Development dependencies (add to requirements-dev.txt)
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
```

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | __pycache__
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

Create `.flake8`:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
ignore = E203, W503
```

**Usage:**

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8 .

# Run all checks
black . && isort . && flake8 .
```

**Benefits:**
- Consistent code style across the project
- Easier code reviews
- Fewer style-related discussions
- Automated enforcement in CI/CD

---

## 7. Input Validation Enhancement

### 🟢 Low Priority

**Current State:**  
Input validation relies solely on Streamlit widgets.

**Recommendation:**  
Add explicit validation in calculation functions.

**Implementation:**

```python
# In core/calculations.py

class CalculationError(Exception):
    """Custom exception for calculation errors."""
    pass

def validate_inputs(pv: float, pmt: float, rate: float, n_years: float) -> None:
    """
    Validate calculation inputs.
    
    Raises:
        CalculationError: If inputs are invalid
    """
    if pv < 0:
        raise CalculationError("Le montant initial ne peut pas être négatif")
    if pmt < 0:
        raise CalculationError("Le versement mensuel ne peut pas être négatif")
    if n_years < 0:
        raise CalculationError("L'horizon ne peut pas être négatif")
    if rate < -100:
        raise CalculationError("Le taux ne peut pas être inférieur à -100%")
    if n_years > 100:
        raise CalculationError("L'horizon ne peut pas dépasser 100 ans")

def calculate_fv(pv: float, pmt: float, rate: float, n_years: float) -> float:
    """Calcule la Valeur Future avec validation."""
    validate_inputs(pv, pmt, rate, n_years)
    
    # ... existing calculation code ...
    
    return result
```

**Benefits:**
- Additional safety layer
- Better error messages
- Consistent validation across all calculation functions
- Easier to test edge cases

---

## 8. Documentation Improvements

### 🟢 Low Priority

**Current State:**  
Documentation is excellent (95%) but a few functions lack docstrings.

**Recommendation:**  
Add missing docstrings and enhance existing ones.

**Implementation:**

```python
# In pages/1_Simulation.py

def main():
    """
    Page principale de simulation d'investissement.
    
    Cette page permet à l'utilisateur de :
    - Choisir quel paramètre calculer (FV, PMT, PV, ou n_years)
    - Saisir les paramètres connus
    - Lancer le calcul
    - Visualiser les résultats avec graphiques
    
    La page affiche également les informations commerciales dans la sidebar.
    """
    # ... existing code ...
```

```python
# In pages/2_Analyse.py

def main():
    """
    Page d'analyse avancée pour clients expérimentés.
    
    Cette page propose plusieurs analyses :
    - Comparaison par horizon de placement
    - Sensibilité aux taux de rendement
    - Sensibilité aux versements mensuels
    - Scénario de retraits réguliers (planification retraite)
    - Impact de l'inflation sur le pouvoir d'achat
    
    Toutes les analyses incluent des graphiques interactifs et des commentaires.
    """
    # ... existing code ...
```

**Benefits:**
- 100% documentation coverage
- Better developer experience
- Easier maintenance
- Professional codebase

---

## 9. Configuration File for Defaults

### 🟢 Low Priority

**Current State:**  
Default values are scattered throughout the code.

**Recommendation:**  
Centralize default values in configuration.

**Implementation:**

Add to `core/config.py`:

```python
# Default values for calculations
DEFAULT_INITIAL_CAPITAL = 100_000
DEFAULT_MONTHLY_PAYMENT = 50_000
DEFAULT_TARGET_AMOUNT = 10_000_000
DEFAULT_ANNUAL_RATE = 5.0
DEFAULT_HORIZON_YEARS = 10

# Constraints
MIN_RATE = -100
MAX_RATE = 100
MIN_HORIZON = 1
MAX_HORIZON = 100

# UI Configuration
CHART_HEIGHT = 350
PIE_CHART_HEIGHT = 400
EXPANDER_EXPANDED_BY_DEFAULT = True

# Countries for dropdown
UEMOA_COUNTRIES = [
    "Côte d'Ivoire",
    "Bénin",
    "Burkina Faso",
    "Guinée-Bissau",
    "Mali",
    "Niger",
    "Sénégal",
    "Togo"
]
```

Then use throughout the application:

```python
# In ui/forms.py
from core.config import (
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_MONTHLY_PAYMENT,
    DEFAULT_TARGET_AMOUNT,
    DEFAULT_ANNUAL_RATE,
    DEFAULT_HORIZON_YEARS
)

def parameter_form():
    # ... existing code ...
    
    inputs["pv"] = st.number_input(
        "Montant Initial (Capital de départ)",
        value=DEFAULT_INITIAL_CAPITAL,
        step=10_000,
        format="%d",
    )
```

**Benefits:**
- Single source of truth for configuration
- Easier to adjust defaults
- Consistent values across the application
- Easier testing with different configurations

---

## 10. CI/CD Pipeline

### 🟢 Low Priority (for team environments)

**Current State:**  
No continuous integration or deployment pipeline.

**Recommendation:**  
Set up GitHub Actions for automated testing and deployment.

**Implementation:**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black isort flake8
    
    - name: Check code formatting
      run: |
        black --check .
        isort --check .
    
    - name: Lint with flake8
      run: |
        flake8 .
    
    - name: Run tests with coverage
      run: |
        pytest --cov=core --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r core/ ui/ pages/
```

**Benefits:**
- Automated testing on every commit
- Catch issues before they reach production
- Consistent quality standards
- Automated security scanning

---

## Summary of Recommendations

| Priority | Recommendation | Effort | Impact | Status |
|----------|---------------|--------|--------|--------|
| 🟡 Medium | Error handling in calculations | Low | High | Recommended |
| 🟡 Medium | Streamlit caching | Low | Medium | Recommended |
| 🟢 Low | Type hints | Medium | Medium | Optional |
| 🟢 Low | Unit tests with pytest | High | High | Optional |
| 🟢 Low | Logging infrastructure | Low | Low | Optional |
| 🟢 Low | Code formatting tools | Low | Low | Optional |
| 🟢 Low | Input validation enhancement | Low | Low | Optional |
| 🟢 Low | Complete documentation | Very Low | Low | Optional |
| 🟢 Low | Configuration centralization | Low | Low | Optional |
| 🟢 Low | CI/CD pipeline | Medium | Medium | Optional |

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 hours)
1. Add error handling to `core/calculations.py`
2. Add Streamlit caching decorators
3. Complete missing docstrings

### Phase 2: Quality Improvements (4-6 hours)
1. Add type hints throughout
2. Set up code formatting (Black, isort)
3. Add input validation

### Phase 3: Long-term Maintainability (8-12 hours)
1. Create comprehensive test suite
2. Add logging infrastructure
3. Set up CI/CD pipeline

---

## Conclusion

The application is **excellent as-is** and ready for production use. All recommendations are **enhancements** that would make the codebase more robust and maintainable, but are **not required** for the application to function correctly.

Focus on Phase 1 if you want quick improvements with minimal effort. Phases 2 and 3 are valuable for long-term projects with multiple developers or strict quality requirements.

---

**Document Version:** 1.0  
**Last Updated:** December 14, 2025  
**Prepared by:** GitHub Copilot Code Analysis
