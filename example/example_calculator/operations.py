# -*- coding: utf-8 -*-

"""Basic arithmetic and mathematical operations."""

from __future__ import annotations

import math


def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of two numbers."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of two numbers.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    """Return base raised to the power of exponent."""
    return math.pow(base, exponent)


def sqrt(value: float) -> float:
    """Return the square root of a non-negative number.

    Raises:
        ValueError: If value is negative.
    """
    if value < 0:
        raise ValueError("Cannot compute square root of a negative number")
    return math.sqrt(value)


def factorial(n: int) -> int:
    """Return the factorial of a non-negative integer.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return math.factorial(n)
