# pylint: disable=empty-docstring, missing-class-docstring, fixme
# pylint: disable=missing-function-docstring, missing-module-docstring

# guitest: skip
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from typing import Callable, Optional

from guidata.guitest import get_test_package  # type: ignore

from moduletester import config as cfg

from .model import Module, TestSuite
from .serializer import dumper, loader

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    ignore_unknown_options=True,
    allow_extra_args=True,
)


@dataclass
class TestManager:
    module: Optional[Module] = None
    moduletester_path: Optional[str] = None

    test_suite: TestSuite = field(init=False)
    up_to_date: bool = field(init=False, default=True)

    _config_conflict_err: Optional[cfg.ConfigConflictError] = field(
        init=False, default=None
    )
    _config_path_val_err: Optional[cfg.InvalidPathError] = field(
        init=False, default=None
    )

    _category: str = "all"
    _template_path: str = ""

    def __post_init__(self):
        mod = self.module
        if (mod is None and self.moduletester_path is None) or (
            mod is not None and self.moduletester_path is not None
        ):
            raise ValueError("One argument should be None")

        elif mod is not None:
            print(self._category)
            test_suite = self._try_load_testsuite(
                lambda: TestSuite(mod, _category=self._category)
            )
            if test_suite is None:
                return

            self.test_suite = test_suite

            if self._template_path == "":
                self._template_path = os.path.join(mod.path, "template.moduletester")

            dumper(self._template_path, self.test_suite)
            print(f"Template created in '{self._template_path}'")

        elif (mod_p := self.moduletester_path) is not None:
            test_suite = self._try_load_testsuite(lambda: loader(mod_p))

            if test_suite is None:
                return

            self.module = test_suite.package

            test_package = get_test_package(self.module.module)
            for test in test_suite.tests:
                test.retrieve_category(test_package)

            self.test_suite = test_suite
            self.up_to_date = True

    def _try_load_testsuite(
        self, test_suite_init: Callable[[], TestSuite | None]
    ) -> TestSuite | None:
        try:
            return test_suite_init()  # type: ignore
        except cfg.ConfigConflictError as e:
            self._config_conflict_err = e
            return None
        except cfg.InvalidPathError as e:
            self._config_path_val_err = e
            return None

    def get_missing_modules(self) -> list[Module]:
        return self.test_suite.get_missing_modules()

    def get_errored_modules(self) -> list[Module]:
        return self.test_suite.get_errored_modules()

    def reload(self):
        """ """
        self.test_suite.reset()

    def refresh_package(self, category: Optional[str] = None):
        self.test_suite.refresh_package(category)

    def save_as(self, moduletester_path: str):
        """ """
        backup_file = moduletester_path + ".bkp"
        shutil.copy(moduletester_path, backup_file)
        dumper(moduletester_path, self.test_suite)
        self.moduletester_path = moduletester_path
        os.remove(backup_file)

    def save(self):
        """ """
        self.save_as(self.moduletester_path or "")

    def open(self, moduletester_path: str):
        """ """
        test_suite = loader(moduletester_path)
        self.test_suite = test_suite

    def pre_export(self, basedir: str, model: str):
        basedir = os.path.abspath(basedir)
        model_path = os.path.join(basedir, model)
        os.makedirs(model_path, exist_ok=True)

    def get_conf_conflict_err(self) -> Optional[cfg.ConfigConflictError]:
        return self._config_conflict_err

    def get_conf_path_val_err(self) -> Optional[cfg.InvalidPathError]:
        return self._config_path_val_err
