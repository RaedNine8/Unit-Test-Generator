"""
Basic test file for the calculator.
"""
import pytest
from test_calculator import add, Calculator

def test_add_basic():
    """Test basic addition."""
    assert add(2, 3) == 5
    assert add(0, 0) == 0

def test_calculator_basic():
    """Test basic calculator functionality."""
    calc = Calculator()
    result = calc.calculate('+', 5, 3)
    assert result == 8
