"""Tests for the serializer module."""

# pylint: disable=missing-class-docstring,missing-function-docstring
from __future__ import annotations

from datetime import datetime, timedelta

from moduletester.serializer import (
    DateTimeSerializer,
    TimedeltaSerializer,
)


class TestDateTimeSerializer:
    def test_roundtrip(self):
        dt = datetime(2026, 5, 20, 14, 30, 45, 123456)
        s = DateTimeSerializer()
        assert s.deserialize(s.serialize(dt)) == dt

    def test_format(self):
        dt = datetime(2026, 1, 2, 3, 4, 5, 678900)
        s = DateTimeSerializer()
        assert s.serialize(dt) == "02/01/26 03:04:05.678900"


class TestTimedeltaSerializer:
    def test_roundtrip(self):
        td = timedelta(hours=1, minutes=30, seconds=15)
        s = TimedeltaSerializer()
        assert s.deserialize(s.serialize(td)) == td

    def test_serialize_seconds(self):
        td = timedelta(seconds=90.5)
        s = TimedeltaSerializer()
        assert s.serialize(td) == 90.5
