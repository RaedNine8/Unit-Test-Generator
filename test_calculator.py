"""
Simple calculator module for testing the Cover Agent.
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def is_even(number):
    """Check if a number is even."""
    return number % 2 == 0

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        """Perform calculation."""
        if operation == '+':
            result = add(a, b)
        elif operation == '-':
            result = subtract(a, b)
        elif operation == '*':
            result = multiply(a, b)
        elif operation == '/':
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append(f"{a} {operation} {b} = {result}")
        return result
    
    def get_history(self):
        """Get calculation history."""
        return self.history.copy()
