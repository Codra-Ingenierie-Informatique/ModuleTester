# pylint: disable=empty-docstring, missing-class-docstring, keyword-arg-before-vararg
# pylint: disable=missing-function-docstring, missing-module-docstring
# guitest: skip

import contextlib
import importlib
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
from importlib import metadata
from types import ModuleType

# cannot import __future__.annotations because it breaks the ModuleType import for some
# reason. The line: 'loader(self.moduletester_path)' return a string instead of a
# module
from typing import Dict, List, Optional, Tuple, Union

import pypandoc
from guidata.configtools import get_image_file_path
from guidata.guitest import TestModule, get_test_package, get_tests  # type: ignore

import moduletester.module_not_found as empty_module
from moduletester import config
from moduletester.config import _
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


class ModuleErrorType(ModuleType):
    """Base class for module errors."""


class ModuleNotFoundType(ModuleErrorType):
    """Module proxy to handle missing modules cleanly.

    Args:
        name: The name of the missing module.
    """

    __file__ = empty_module.__file__
    __path__ = [os.path.dirname(empty_module.__file__)]

    def __init__(self, name: str):
        super().__init__(name)
        self.__doc__ = empty_module.__doc__


class ModuleInternalErrorType(ModuleErrorType):
    """Module proxy to handle module erros at import (error in the module).

    Args:
        test_package: The test package from which the import was tried.
        path: The path of the errored module.
        error: The error message.
    """

    def __init__(self, test_package: ModuleType, path: str, error: str):
        test_pkg_file = test_package.__file__
        if test_pkg_file is None:
            raise ValueError(
                "Attribute test_package.__file__ is None instead of a str path."
            )
        test_package_path = os.path.dirname(os.path.realpath(test_pkg_file))
        name = os.path.relpath(path, test_package_path)
        subpkgname = test_package.__name__
        if len(name.split(os.sep)) > 1:
            subpkgname += "." + ".".join(name.split(os.sep)).rstrip(".py")
        super().__init__(subpkgname)
        self.__file__ = path
        self.__path__ = [os.path.dirname(path)]
        self.__doc__ = (
            _("This package encountered the following error during import:\n%s") % error
        )


# @xxx.register
class Module:
    """ """

    def __init__(self, module: ModuleType):
        if module.__name__ in sys.modules and not isinstance(module, ModuleErrorType):
            module = importlib.reload(module)
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
    def doc(self) -> str:
        return self.module.__doc__ or ""

    @property
    def author(self) -> str:
        try:
            return metadata.metadata(self.module.__name__)["Author"] or ""
        except metadata.PackageNotFoundError as e:
            print(e)
            return ""

    @property
    def root_path(self) -> str:
        path = self.module.__file__
        if path is not None:
            # if os.path.basename(path) == "__init__.py":
            #     path = os.path.join(path, "..")
            return os.path.abspath(os.path.join(path, ".."))
        else:
            return os.path.join(*self.module.__path__)

    @classmethod
    def __deserialize__(cls, obj: str) -> "Module":
        try:
            return cls(sys.modules[obj])
        except KeyError:
            try:
                __import__(obj)
                return cls(sys.modules[obj])
            except ModuleNotFoundError as e:
                print(e)
                return cls(ModuleNotFoundType(obj))


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

    ACCEPTED = "accepted", "green-check-square.png"
    ACCEPTED_WITH_RESERVES = "accepted with reserves", "yellow-check-square.png"
    SKIPPED = "skipped", "skip.png"
    REJECTED = "rejected", "rejected.png"
    NO_RESULT = "no result", "unknown.png"

    icon_path: str

    def __new__(cls, label: str, icon_name: Optional[str] = None):
        obj = object.__new__(cls)
        obj._value_ = label
        obj.icon_path = get_image_file_path(icon_name or "")
        return obj

    def __init__(self, label: str, __ignored=None) -> None: ...

    """Fake init method used to get the correct linting/auto-completion."""

    def format(self) -> str:
        return self.name.replace("_", " ")


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

    def __post_init__(self):
        if isinstance(self.last_run, str):
            self.last_run = datetime.strptime(self.last_run, "%d/%m/%y %H:%M:%S.%f")

    @property
    def result_name(self) -> str:
        return self.result.name.replace("_", " ")

    @property
    def status_name(self) -> str:
        return self.status.name.replace("_", " ")


FormatArgsType = Tuple[str, ...]


@DataclassSerializer.register
@dataclass
class Test:
    """ """

    package: Module
    description: str = ""
    result: Optional[TestResult] = None
    command_args: str = ""
    command_timeout: int = 0
    run_opts: List[str] = field(default_factory=list)
    is_valid: bool = True
    _is_new_message: bool = False
    _is_new_error: bool = False
    _end_time: float = 0
    _is_running: bool = False
    _forced: bool = False
    _is_skipped: bool = False
    _is_visible: bool = False
    _proc: Optional[subprocess.Popen] = None
    _tf: float = 0
    _command: str = ""
    _is_stopped: bool = False
    _cached_description: Dict[FormatArgsType, str] = field(default_factory=dict)
    _max_cache_size = 10

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
        self._command = self.build_command()
        return self._command

    def is_visible(self):
        return self._is_visible

    def set_visible(self, is_visible):
        self._is_visible = is_visible

    def is_skipped(self):
        return self._is_skipped

    def set_skipped(self, is_skipped):
        self._is_skipped = is_skipped

    def is_message_new(self):
        return self._is_new_message

    def is_error_new(self):
        return self._is_new_error

    def set_error_state(self, is_new: bool):
        self._is_new_error = is_new

    def set_message_state(self, is_new: bool):
        self._is_new_message = is_new

    def __enter__(self):
        """ """

    def __exit__(self, _type, _value, _traceback):
        """ """
        forced = self._end_time is None or self._end_time > self._tf
        if not forced:
            self.stop(False)
        assert self.result is not None and self._proc is not None

        self.result.execution_duration = round(
            time.time() - (self._tf - self.command_timeout), 2
        )
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
                if sys.platform == "win32":
                    self._proc.send_signal(signal.CTRL_BREAK_EVENT)
                elif sys.platform == "linux":
                    os.killpg(self._proc.pid, signal.SIGKILL)
                self._is_stopped = True
                self._is_running = False
            else:
                self.wait_kill()
                self._is_running = False

    def build_command(self) -> str:
        """Builds the command to run the test.

        Returns:
            Command line as a string
        """
        command = [
            sys.executable,
            "-u",
            "-X",
            "utf8",
            f"{self.package.module.__file__}",
        ]

        if self.command_args:
            command.extend(shlex.split(self.command_args))
        self._tf = time.time() + self.command_timeout

        return shlex.join(command).replace("'", '"')

    def run(self):
        """Runs test"""
        if self._proc is None:
            self._is_stopped = False
            self._end_time = 0
            os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)

            if self.result is None:
                self.result = TestResult(StatusEnum.NOT_EXECUTED)
            self.result.error_msg = ""
            self.result.output_msg = ""

            self._command = self.build_command()

            self._proc = subprocess.Popen(
                self._command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32"
                    else 0
                ),
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                preexec_fn=os.setpgrp if sys.platform == "linux" else None,
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
            and (self.command_timeout <= 0 or time.time() < self._tf)
            and self._proc.returncode is None
            and not self._is_stopped
        )

    def communicate(self, timeout: float = 1):
        """ """
        if self._proc is not None and self.result is not None:
            with contextlib.suppress(subprocess.TimeoutExpired):
                last_outs, last_errs = self._proc.communicate(timeout=timeout)

                if last_outs is not None:
                    self.result.output_msg += last_outs
                if last_errs is not None:
                    self.result.error_msg += last_errs

        else:
            raise subprocess.SubprocessError("No subprocess running.")

    def wait_kill(self):
        """ """
        if self._proc is not None:
            self._proc.kill()
            while self._proc is not None and self._proc.returncode is None:
                with contextlib.suppress(subprocess.TimeoutExpired):
                    self.communicate(timeout=0.5)

    def get_description(self) -> str:
        return self.package.doc or ""

    def get_fmt_description(
        self, fmt: str, extra_args: Optional[List[str]] = None, use_cached: bool = True
    ) -> str:
        """Get the description of the test in the specified format.

        Args:
            fmt: format to convert the docstring into.
            extra_args: Extra Pandoc args. Defaults to None.
            use_cached: Use a cached version of the formated description.
             Defaults to True.

        Returns:
            The description of the test in the specified format.
        """
        if extra_args is None:
            extra_args = []
        extra_args.append(f"--resource-path={self.package.root_path}")
        fmt_args = (fmt, *extra_args)
        doc = self._cached_description.get(fmt_args, None) if use_cached else None
        if doc is None:
            doc = pypandoc.convert_text(
                self.get_description() or "",
                fmt,
                format=config.PACKAGE_CONF["general"].docstring_fmt,
                extra_args=extra_args,
            )
            self._cached_description[fmt_args] = doc
        return doc

    def _get_pandoc_extra_args(
        self,
        standalone=False,
        embeded=True,
        shift_header=0,
        apply_style: bool = False,
        quiet=True,
    ) -> List[str]:
        """Simply computes a list of extra arguments for pandoc.

        Args:
            standalone: Generate a standalone document. Defaults to False.
            embeded: Embed all ressources in the document. Defaults to True.
            shift_header: Shift header level by specified value. Defaults to 0.
            apply_style: Apply the given styles from the css file given in config.
             Defaults to False.
            quiet: Flag for pandoc verbose level. Defaults to True.

        Returns:
            List of extra arguments for pandoc.
        """
        extra_args = []
        if standalone:
            extra_args.append("--standalone")
        if embeded:
            extra_args.append("--embed-resources")
        if shift_header != 0:
            extra_args.append(f"--shift-heading-level-by={shift_header}")
        if apply_style:
            extra_args.append(f"--css={config.PACKAGE_CONF['export'].get_css_style()}")
        if quiet:
            extra_args.append("--quiet")
        return extra_args

    def get_html_description(
        self,
        standalone=False,
        embeded=True,
        shift_header=0,
        apply_style: bool = False,
        use_cached: bool = True,
    ) -> str:
        """Get the description of the test in HTML format.

        Args:
            standalone: Generate a standalone document. Defaults to False.
            embeded: Embed all ressources in the document. Defaults to True.
            shift_header: Shift header level by specified value. Defaults to 0.
            apply_style: Apply the given styles from the css file given in config.
             Defaults to False.
            use_cached: Use a cached version of the formated description.
             Defaults to True.

        Returns:
            The description of the test in HTML format.
        """
        extra_args = self._get_pandoc_extra_args(
            standalone, embeded, shift_header, apply_style, True
        )
        return self.get_fmt_description(
            "html", extra_args=extra_args, use_cached=use_cached
        )

    def get_txt_description(
        self, standalone=False, embeded=True, shift_header=0
    ) -> str:
        """Get the description of the test in plain text format.

        Args:
            standalone: Generate a standalone document. Defaults to False.
            embeded: Embed all ressources in the document. Defaults to True.
            shift_header: Shift header level by specified value. Defaults to 0.

        Returns:
            The description of the test in plain text format.
        """
        extra_args = self._get_pandoc_extra_args(standalone, embeded, shift_header)

        return self.get_fmt_description("plain", extra_args=extra_args)

    def get_md_description(self, standalone=False, embeded=True, shift_header=0) -> str:
        """Get the description of the test in markdown format.

        Args:
            standalone: Generate a standalone document. Defaults to False.
            embeded: Embed all ressources in the document. Defaults to True.
            shift_header: Shift header level by specified value. Defaults to 0.

        Returns:
            The description of the test in markdown format.
        """
        extra_args = self._get_pandoc_extra_args(standalone, embeded, shift_header)

        return self.get_fmt_description("md", extra_args=extra_args)

    def get_images(self, image_dirs: List[str]) -> List[str]:
        """ """
        return get_image_path(self.package.last_name, image_dirs)

    def retrieve_category(self, test_package: ModuleType):
        path = self.package.module.__file__
        test_module = TestModule(test_package, path)
        self.set_visible(test_module.is_visible())
        self.set_skipped(test_module.is_skipped())

    def get_code_snippet(self, test_package: ModuleType):
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

    def result_binary_label(self) -> Tuple[int, ...]:
        """Computes the binary label of the result.

        Returns:
            Tuple of int, 1 if the result is the same as the test result, 0 otherwise.
        """
        return tuple(
            map(
                lambda res: (
                    1 if (self.result is not None and self.result.result is res) else 0
                ),
                ResultEnum,
            )
        )


@DataclassSerializer.register
@dataclass
class TestSuite:
    """ """

    package: Module
    author: str = ""
    description: str = ""
    last_run: Optional[datetime] = None

    tests: List[Test] = field(default_factory=list)

    _category: str = config.PACKAGE_CONF["general"].category
    _running_test: Optional[Test] = None

    def __post_init__(self) -> None:
        if len(self.tests) == 0:
            self.reset()
        self.author = self.package.author
        self.description = self.package.doc
        config.load_package_conf(self.package.root_path)

    def get_fmt_description(self, fmt="html", extra_args=None):
        """Return the description of the test suite in the specified format.

        Args:
            fmt: format to convert the docstring into. Defaults to "html".
            extra_args: Extra Pandoc args. Defaults to None.

        Returns:
            The description of the test suite in the specified format.
        """
        if extra_args is None:
            extra_args = []
        extra_args.append(f"--resource-path={self.package.root_path}")
        return pypandoc.convert_text(
            self.description or "",
            fmt,
            format=config.PACKAGE_CONF["general"].docstring_fmt,
            extra_args=extra_args,
        )

    @property
    def package_name(self) -> str:
        return self.package.module.__name__

    @property
    def running_test(self) -> Optional[Test]:
        return self._running_test

    def reset(self) -> None:
        """category must be "all", "visible", or "batch"."""
        self.tests.clear()
        for test_module in get_tests(self.package.module, self._category):
            if not test_module.is_valid():
                test_module.module = self.load_errored_test_module(test_module)
            test = Test.build_from_test_module(test_module)
            self.tests.append(test)

    def refresh_package(self, category: Optional[str] = None) -> None:
        """Refresh the package and its tests.

        Args:
            category: category must be "all", "visible", or "batch". Defaults to None.
        """
        exising_tests: Dict[str, Test] = {
            test.package.full_name: test for test in self.tests
        }
        self.tests.clear()
        category = category or self._category
        for test_module in get_tests(self.package.module, category):
            if not test_module.is_valid():
                test_module.module = self.load_errored_test_module(test_module)
            test = Test.build_from_test_module(test_module)
            if old_test := exising_tests.get(test.package.full_name, None):
                test.result = old_test.result
                test.command_args = old_test.command_args
                test.command_timeout = old_test.command_timeout
                test.run_opts = old_test.run_opts

            self.tests.append(test)
        self.__post_init__()

    def load_errored_test_module(
        self, test_module: TestModule
    ) -> ModuleInternalErrorType:
        """Load the errored test module.

        Args:
            test_module: The test module that errored during import.

        Returns:
            The errored test module wrapped in a ModuleType proxy class.
        """
        package = get_test_package(self.package.module)
        return ModuleInternalErrorType(package, test_module.path, test_module.error_msg)

    # Run related methods
    def run(
        self,
        category: str = "all",
        pattern: str = "",
        timeout: Optional[int] = None,
        test_args: Optional[str] = None,
    ) -> None:
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
                    while test.is_running():
                        test.communicate(0.5)
                    # Kills the test if still running, otherwise the process could keep
                    # running in the background
                    test.stop()
                    test.end_time = time.time()
                self._running_test = None

    def terminate_run(self) -> None:
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
        # path = str(package.module.__file__)
        # if pattern in ("", "*") or pattern in path or pattern in package.full_name:
        if pattern in ("", "*") or pattern == package.last_name:
            return True

        return False

    def group_tests(self) -> Dict[str, List[Test]]:
        assert self.tests

        diff_path = defaultdict(list)
        for test in self.tests:
            diff_path[str(test.package.module.__package__)].append(test)

        return diff_path

    def get_missing_modules(self) -> List[Module]:
        """Get the list of missing modules.

        Returns:
            List of missing modules.
        """
        missing_modules_list = [
            test.package
            for test in self.tests
            if isinstance(test.package.module, ModuleNotFoundType)
        ]
        return missing_modules_list

    def get_errored_modules(self) -> list[Module]:
        """Get the list of errored modules (for which the import failed).

        Returns:
            List of errored modules.
        """
        error_modules_list = [
            test.package
            for test in self.tests
            if isinstance(test.package.module, ModuleInternalErrorType)
        ]
        return error_modules_list

    def results_binary_labels(self) -> List[Tuple[int, ...]]:
        """Computes the binary labels of the results.

        Returns:
            List of tuples of int, 1 if the result is the same as the test result,
             0 otherwise.
        """
        return [test.result_binary_label() for test in self.tests]

    def results_count(self) -> Tuple[int, ...]:
        """Computes the of test result by result kind.

        Returns:
            Tuple of int, the count of test result by result kind.
        """
        results = self.results_binary_labels()
        return tuple(map(sum, zip(*results)))
