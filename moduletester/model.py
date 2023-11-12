# pylint: disable=empty-docstring, missing-class-docstring, keyword-arg-before-vararg
# pylint: disable=missing-function-docstring, missing-module-docstring
# guitest: skip
import os
import shlex
import signal
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from types import ModuleType
from typing import Dict, List, Optional, Union

from guidata.guitest import TestModule, get_tests  # type: ignore

from moduletester.python_helpers import get_image_path  # type: ignore
from moduletester.serializer import (
    DataclassSerializer,
    EnumSerializer,
    ValueSerializerBase,
)

# ============================================================================
#
#       Helpers class
#
# ============================================================================


# @xxx.register
class Module:
    """ """

    def __init__(self, module: ModuleType):
        self.module = module

    def __copy__(self):
        return self.module.__name__

    def __deepcopy__(self, memo):
        return self.module.__name__

    def __str__(self) -> str:
        return f"{type(self).__qualname__}(module={self.module})"

    def __eq__(self, __value: object) -> bool:
        ret = isinstance(__value, Module) and (self.module == __value.module)
        return ret

    def __serialize__(self) -> str:
        return self.module.__name__

    @property
    def full_name(self) -> str:
        return self.module.__name__

    @property
    def last_name(self) -> str:
        return self.full_name.split(".")[-1]

    @property
    def name_from_source(self) -> str:
        name = self.full_name.split(".")[1:]
        return ".".join(name)

    @property
    def path(self) -> str:
        return self.module.__path__[0]

    @property
    def doc(self) -> Optional[str]:
        if self.module.__doc__ is None:
            return None
        return self.module.__doc__.strip()

    @property
    def root_path(self) -> Optional[str]:
        path = self.module.__file__
        if path is not None:
            if os.path.basename(path) == "__init__.py":
                path = os.path.join(path, "..")
            path = os.path.abspath(os.path.join(path, ".."))

        return path

    @classmethod
    def __deserialize__(cls, obj: str) -> "Module":
        try:
            return cls(sys.modules[obj])
        except KeyError:
            __import__(obj)
            return cls(sys.modules[obj])


class ModuleSerializer(ValueSerializerBase[Module, str]):
    def serialize(self, obj: Module) -> str:
        return obj.__serialize__()

    def deserialize(self, obj: str) -> Module:
        return Module.__deserialize__(obj)


# ============================================================================
#
#       Enums
#
# ============================================================================


@EnumSerializer.register
class StatusEnum(Enum):
    """Status value for a test."""

    EXECUTED = "executed"
    NOT_EXECUTED = "not executed"
    ABORTED = "aborted"


@EnumSerializer.register
class ResultEnum(Enum):
    """Results value for a test."""

    ACCEPTED = "accepted"
    ACCEPTED_WITH_RESERVES = "accepted with reserves"
    SKIPPED = "skipped"
    REJECTED = "rejected"
    NO_RESULT = "no result"


# ============================================================================
#
#       Dataclasses
#
# ============================================================================


@DataclassSerializer.register
@dataclass
class TestResult:
    """ """

    status: StatusEnum
    result: ResultEnum = ResultEnum.NO_RESULT
    execution_duration: Optional[Union[timedelta, float]] = None
    last_run: Optional[datetime] = None
    comment: str = ""
    output_msg: str = ""
    error_code: Optional[int] = None
    error_msg: str = ""

    @property
    def result_name(self) -> str:
        return self.result.name.replace("_", " ")

    @property
    def status_name(self) -> str:
        return self.status.name.replace("_", " ")


@DataclassSerializer.register
@dataclass
class Test:
    """ """

    package: Module
    description: str = ""
    result: Optional[TestResult] = None
    command_args: str = ""
    command_timeout: int = 86400
    run_opts: List[str] = field(default_factory=list)
    is_valid: bool = True
    _end_time: float = 0
    _is_running: bool = False
    _forced: bool = False
    _is_skipped: bool = False
    _is_visible: bool = False
    _proc: Optional[subprocess.Popen] = None
    _tf: float = 0
    _command: str = ""
    _is_stopped: bool = False

    def __post_init__(self):
        if self.description == "":
            self.description = self.get_description()

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        self._end_time = end_time

    @property
    def command(self):
        return self._command

    def is_visible(self):
        return self._is_visible

    def set_visible(self, is_visible):
        self._is_visible = is_visible

    def is_skipped(self):
        return self._is_skipped

    def set_skipped(self, is_skipped):
        self._is_skipped = is_skipped

    def __enter__(self):
        """ """

    def __exit__(self, _type, _value, _traceback):
        """ """
        forced = self._end_time > self._tf
        if not forced:
            self.stop(False)
        assert self.result is not None

        self.result.execution_duration = time.time() - (self._tf - self.command_timeout)
        self.result.error_code = self._proc.returncode
        self.result.last_run = datetime.now()

        if self._forced:
            self.result.status = StatusEnum.ABORTED
        else:
            self.result.status = StatusEnum.EXECUTED

        self._proc = None

    def start(self) -> "Test":
        """ """
        self.run()

        return self

    def stop(self, forced: bool = False):
        """ """
        if self._proc is not None and self._is_running:
            self._forced = forced
            if forced:
                self._proc.send_signal(signal.CTRL_BREAK_EVENT)
                self._is_stopped = True
                self._is_running = False
            else:
                self.wait_kill()
                self._is_running = False

    def run(self):
        """Runs test"""
        if self._proc is None:
            self._is_stopped = False
            self._end_time = None
            os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
            path = self.package.module.__file__

            if self.result is None:
                self.result = TestResult(StatusEnum.NOT_EXECUTED)
            self.result.error_msg = ""
            self.result.output_msg = ""

            command = [sys.executable, "-u", "-X", "utf8", f"{path}"]

            if self.command_args:
                command.append(self.command_args)
            self._tf = time.time() + self.command_timeout

            self._command = shlex.join(command).replace("'", '"')

            self._proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                bufsize=1,
                universal_newlines=True,
            )
            self._is_running = True
        else:
            print("Process is already running. Restarting process.")
            self.restart()

    def restart(self):
        if self._proc is not None:
            self.stop(forced=True)
        self.run()

    def is_running(self) -> bool:
        """ """
        return (
            self._proc is not None
            and time.time() < self._tf
            and self._proc.returncode is None
            and not self._is_stopped
        )

    def communicate(self, timeout: float = 1):
        """ """
        if self._proc is not None and self.result is not None:
            try:
                last_outs, last_errs = self._proc.communicate(timeout=timeout)

                # self.result.output_msg += last_outs.decode("utf-8")
                # self.result.error_msg += last_errs.decode("utf-8")

                self.result.output_msg += last_outs
                self.result.error_msg += last_errs

            except subprocess.TimeoutExpired:
                pass

        else:
            raise subprocess.SubprocessError("No subprocess running.")

    def wait_kill(self):
        """ """
        if self._proc is not None:
            self._proc.kill()
            while self._proc is not None and self._proc.returncode is None:
                try:
                    self.communicate(timeout=0.5)
                except subprocess.TimeoutExpired:
                    pass

    def get_description(self) -> Optional[str]:
        return self.package.doc

    def get_images(self, image_dirs: List[str]) -> List[str]:
        """ """
        return get_image_path(self.package.last_name, image_dirs)

    def retrieve_category(self, test_package: Module):
        path = self.package.module.__file__
        test_module = TestModule(test_package, path)
        self.set_visible(test_module.is_visible())
        self.set_skipped(test_module.is_skipped())

    def get_code_snippet(self, test_package: Module):
        path = self.package.module.__file__
        test_module = TestModule(test_package, path)

        return test_module.get_contents()

    @classmethod
    def build_from_test_module(cls, test_module: TestModule) -> "Test":
        """ """
        module = test_module.module
        test = cls(Module(module))
        test.is_valid = test_module.is_valid()
        test._is_skipped = test_module.is_skipped()
        test._is_visible = test_module.is_visible()
        return test


@DataclassSerializer.register
@dataclass
class TestSuite:
    """ """

    package: Module
    author: str = ""
    description: str = ""
    last_run: Optional[datetime] = None

    tests: Optional[List[Test]] = None
    _category: str = "all"
    _running_test: Optional[Test] = None

    @property
    def package_name(self):
        return self.package.module.__name__

    @property
    def running_test(self):
        return self._running_test

    def __post_init__(self):
        if self.tests is None:
            self.tests = []
            self.reset()

    def reset(self):
        """category must be "all", "visible", or "batch"."""
        self.tests.clear()
        for test_module in get_tests(self.package.module, self._category):
            test = Test.build_from_test_module(test_module)
            self.tests.append(test)

    # Run related methods
    def run(
        self,
        category: str = "all",
        pattern: str = "",
        timeout: Optional[int] = None,
        test_args: Optional[str] = None,
    ):
        """"""
        assert self.tests
        self.last_run = datetime.now()
        for test in self.tests:
            if self.should_run(test, category, pattern):
                print(f"Running test {test.package.module.__file__}")
                if timeout is not None:
                    test.command_timeout = timeout
                if test_args is not None:
                    test.command_args = test_args

                self._running_test = test
                with test.start():
                    while self.running_test.is_running():
                        self.running_test.communicate(0.5)
                    self.running_test.end_time = time.time()
                self._running_test = None

    def terminate_run(self):
        pass

    def should_run(self, test: Test, category: str = "all", pattern: str = "") -> bool:
        package = test.package
        called = self.is_called(package, pattern)

        is_valid = (
            category == "all"
            or (category == "visible" and test.is_visible())
            or (category == "batch" and not test.is_skipped())
        )

        return is_valid and called

    def is_called(self, package: Module, pattern: str = "") -> bool:
        path = str(package.module.__file__)
        if pattern in ("", "*") or pattern in path or pattern in package.full_name:
            return True

        return False

    def group_tests(self) -> Dict[str, List[Test]]:
        assert self.tests

        diff_path = defaultdict(list)
        for test in self.tests:
            diff_path[str(test.package.module.__package__)].append(test)

        return diff_path
