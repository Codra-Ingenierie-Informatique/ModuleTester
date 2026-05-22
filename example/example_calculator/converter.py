# -*- coding: utf-8 -*-

"""Unit conversion functions (temperature, distance)."""

from __future__ import annotations

# --- Temperature conversions ---


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32.0) * 5.0 / 9.0


def celsius_to_kelvin(celsius: float) -> float:
    """Convert Celsius to Kelvin.

    Raises:
        ValueError: If the result would be below absolute zero.
    """
    kelvin = celsius + 273.15
    if kelvin < 0:
        raise ValueError("Temperature below absolute zero is not physical")
    return kelvin


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius.

    Raises:
        ValueError: If kelvin is negative.
    """
    if kelvin < 0:
        raise ValueError("Kelvin temperature cannot be negative")
    return kelvin - 273.15


# --- Distance conversions ---


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return feet / 3.28084


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles."""
    return km * 0.621371


def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles / 0.621371
