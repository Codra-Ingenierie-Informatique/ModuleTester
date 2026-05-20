"""Tests for the model module (enums, dataclasses)."""

from __future__ import annotations

from datetime import datetime, timedelta

from moduletester.model import (
    ModuleNotFoundType,
    ResultEnum,
    StatusEnum,
    TestResult,
)
from moduletester.serializer import DataclassSerializer, EnumSerializer


class TestStatusEnum:
    def test_values(self):
        assert StatusEnum.EXECUTED.value == "executed"
        assert StatusEnum.NOT_EXECUTED.value == "not executed"
        assert StatusEnum.ABORTED.value == "aborted"

    def test_serializer_roundtrip(self):
        s = EnumSerializer(StatusEnum)
        for member in StatusEnum:
            assert s.deserialize(s.serialize(member)) == member


class TestResultEnum:
    def test_values(self):
        assert ResultEnum.ACCEPTED.value == "accepted"
        assert ResultEnum.NO_RESULT.value == "no result"

    def test_format(self):
        assert ResultEnum.ACCEPTED_WITH_RESERVES.format() == "ACCEPTED WITH RESERVES"

    def test_serializer_roundtrip(self):
        s = EnumSerializer(ResultEnum)
        for member in ResultEnum:
            assert s.deserialize(s.serialize(member)) == member


class TestTestResult:
    def test_creation_defaults(self):
        tr = TestResult(status=StatusEnum.NOT_EXECUTED)
        assert tr.result == ResultEnum.NO_RESULT
        assert tr.comment == ""
        assert tr.output_msg == ""
        assert tr.error_msg == ""
        assert tr.error_code is None

    def test_serialization_roundtrip(self):
        tr = TestResult(
            status=StatusEnum.EXECUTED,
            result=ResultEnum.ACCEPTED,
            execution_duration=timedelta(seconds=1.5),
            last_run=datetime(2026, 5, 20, 10, 0, 0, 0),
            comment="OK",
        )
        s = DataclassSerializer()
        data = s.serialize(tr)
        restored = s.deserialize(data)
        assert isinstance(restored, TestResult)
        assert restored.status == StatusEnum.EXECUTED
        assert restored.result == ResultEnum.ACCEPTED
        assert restored.comment == "OK"

    def test_properties(self):
        tr = TestResult(
            status=StatusEnum.EXECUTED, result=ResultEnum.ACCEPTED_WITH_RESERVES
        )
        assert tr.result_name == "ACCEPTED WITH RESERVES"
        assert tr.status_name == "EXECUTED"


class TestModuleNotFoundType:
    def test_creation(self):
        m = ModuleNotFoundType("some.missing.module")
        assert m.__name__ == "some.missing.module"
        assert m.__doc__ is not None
