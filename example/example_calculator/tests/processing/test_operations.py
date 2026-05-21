# -*- coding: utf-8 -*-

# guitest: skip

"""Pytest unit tests for example_calculator.operations."""

import math

import pytest
from example_calculator.operations import (
    add,
    divide,
    factorial,
    multiply,
    power,
    sqrt,
    subtract,
)


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -2) == -3

    def test_zero(self):
        assert add(0, 0) == 0


class TestSubtract:
    def test_basic(self):
        assert subtract(10, 4) == 6

    def test_negative_result(self):
        assert subtract(3, 7) == -4


class TestMultiply:
    def test_basic(self):
        assert multiply(3, 4) == 12

    def test_by_zero(self):
        assert multiply(5, 0) == 0


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5.0

    def test_float_result(self):
        assert divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            divide(1, 0)


class TestPower:
    def test_basic(self):
        assert power(2, 3) == 8.0

    def test_zero_exponent(self):
        assert power(5, 0) == 1.0


class TestSqrt:
    def test_basic(self):
        assert sqrt(9) == 3.0

    def test_zero(self):
        assert sqrt(0) == 0.0

    def test_negative(self):
        with pytest.raises(ValueError, match="negative"):
            sqrt(-1)


class TestFactorial:
    def test_basic(self):
        assert factorial(5) == 120

    def test_zero(self):
        assert factorial(0) == 1

    def test_negative(self):
        with pytest.raises(ValueError, match="negative"):
            factorial(-1)
