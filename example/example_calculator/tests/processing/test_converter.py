# -*- coding: utf-8 -*-

# guitest: skip

"""Pytest unit tests for example_calculator.converter."""

import pytest
from example_calculator.converter import (
    celsius_to_fahrenheit,
    celsius_to_kelvin,
    fahrenheit_to_celsius,
    feet_to_meters,
    kelvin_to_celsius,
    km_to_miles,
    meters_to_feet,
    miles_to_km,
)


class TestTemperature:
    def test_celsius_to_fahrenheit(self):
        assert celsius_to_fahrenheit(0) == 32.0
        assert celsius_to_fahrenheit(100) == 212.0

    def test_fahrenheit_to_celsius(self):
        assert fahrenheit_to_celsius(32) == 0.0
        assert fahrenheit_to_celsius(212) == 100.0

    def test_celsius_to_kelvin(self):
        assert celsius_to_kelvin(0) == 273.15
        assert celsius_to_kelvin(-273.15) == 0.0

    def test_celsius_to_kelvin_below_absolute_zero(self):
        with pytest.raises(ValueError, match="absolute zero"):
            celsius_to_kelvin(-300)

    def test_kelvin_to_celsius(self):
        assert kelvin_to_celsius(273.15) == 0.0
        assert kelvin_to_celsius(0) == -273.15

    def test_kelvin_negative(self):
        with pytest.raises(ValueError, match="negative"):
            kelvin_to_celsius(-1)


class TestDistance:
    def test_meters_to_feet(self):
        assert abs(meters_to_feet(1) - 3.28084) < 1e-4

    def test_feet_to_meters(self):
        assert abs(feet_to_meters(3.28084) - 1.0) < 1e-4

    def test_km_to_miles(self):
        assert abs(km_to_miles(1) - 0.621371) < 1e-4

    def test_miles_to_km(self):
        assert abs(miles_to_km(0.621371) - 1.0) < 1e-4
