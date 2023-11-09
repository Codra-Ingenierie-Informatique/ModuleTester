# pylint: disable=empty-docstring, missing-class-docstring, fixme
# pylint: disable=missing-function-docstring, missing-module-docstring

# guitest: skip

import os
from dataclasses import dataclass, field
from importlib import import_module
from typing import Optional

import click
from guidata.guitest import get_test_package  # type: ignore

from .exporter import TestSuiteExporter
from .model import Module, TestSuite
from .python_helpers import rst2odt
from .serializer import dumper, loader

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    ignore_unknown_options=True,
    allow_extra_args=True,
)


@dataclass
class TestBench:
    module: Optional[Module] = None
    testbench_path: Optional[str] = None

    test_suite: TestSuite = field(init=False)
    up_to_date: bool = field(init=False, default=True)

    _category: str = "all"
    _template_path: str = ""

    def __post_init__(self):
        if (self.module is None and self.testbench_path is None) or (
            self.module is not None and self.testbench_path is not None
        ):
            raise ValueError("One argument should be None")

        elif self.module is not None:
            print(self._category)
            self.test_suite = TestSuite(self.module, _category=self._category)

            if self._template_path == "":
                self._template_path = os.path.join(
                    self.module.path, "template.testbench"
                )

            dumper(self._template_path, self.test_suite)
            print(f"Template created in '{self._template_path}'")

        elif self.testbench_path is not None:
            test_suite = loader(self.testbench_path)
            self.module = test_suite.package
            test_package = get_test_package(self.module.module)
            for test in test_suite.tests:
                test.retrieve_category(test_package)

            self.test_suite = test_suite
            self.up_to_date = True

    def reload(self):
        """ """
        self.test_suite.reset()

    def save_as(self, testbench_path):
        """ """
        dumper(testbench_path, self.test_suite)
        self.testbench_path = testbench_path

    def save(self):
        """ """
        dumper(self.testbench_path, self.test_suite)

    def open(self, testbench_path: str):
        """ """
        test_suite = loader(testbench_path)
        self.test_suite = test_suite

    def export(self, basedir: str, model: str):
        if model.lower() in ["rtv", "dtv"]:
            basedir = os.path.abspath(basedir)
            path_to_temp = os.path.join(basedir, model, "tmp")
            path_to_rst = os.path.join(basedir, model, f"{model}.rst")

            os.makedirs(path_to_temp, exist_ok=True)

            exporter = TestSuiteExporter(self.test_suite)
            export_section = (
                exporter.export_section_dtv
                if model == "dtv"
                else exporter.export_section_rtv
            )

            exporter.export(path_to_rst, path_to_temp, export_section)
        else:
            print("model parameter must be in ['rtv', 'dtv']")


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.argument("package")
@click.option(
    "--output", "-o", default="", help="output path for .testbench template file"
)
def template(package: str, output: str = ""):
    """Generate .testbench template file"""
    mod = import_module(package)

    if output != "" and os.path.isdir(output):
        output = os.path.join(output, "template.testbench")
    elif (
        output != ""
        and not os.path.exists(output)
        and not os.path.basename(output).endswith(".testbench")
    ):
        raise ValueError(f"'{output}' is incorrect for output")

    _ = TestBench(Module(mod), _template_path=output)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.argument("testbench_path")
@click.option("--category", "-c", default="all", help="guitest category")
@click.option("save_path", "--save", "-s", default="", help="Path to save result")
@click.option("pattern", "--pattern", "-p", default="", help="test name pattern")
@click.option("--timeout", default=86400, type=int, help="test timeout")
def run(
    ctx,
    testbench_path: str,
    pattern: str = "",
    category: str = "all",
    save_path: str = "",
    timeout: int = 86400,
):
    """Run tests with --test-args"""
    testbench = TestBench(testbench_path=testbench_path)

    if save_path == "":
        save_path = testbench_path
    elif os.path.exists(save_path):
        raise ValueError(f'"{save_path}" already exists')

    args = ""
    if len(ctx.args) != 0:
        args = " ".join(ctx.args)

    testbench.test_suite.run(category, pattern, timeout, args)
    testbench.save_as(save_path)
    print(f"Run saved in {save_path}")


@cli.command()
@click.argument("testbench_path")
@click.option("output_dir", "--output", "-o", default="", help="Output directory")
def dtv(testbench_path: str, output_dir: str = ""):
    """Generate dtv for given .testbench file"""
    testbench = TestBench(testbench_path=testbench_path)
    assert testbench.module

    if output_dir == "":
        output_dir = testbench.module.path

    testbench.export(output_dir, "dtv")
    print(f"DTV exported in {output_dir}")


@cli.command()
@click.argument("testbench_path")
@click.option("output_dir", "--output", "-o", default="", help="Output directory")
def rtv(testbench_path: str, output_dir: str = ""):
    """Generate rtv for given .testbench file"""
    testbench = TestBench(testbench_path=testbench_path)
    assert testbench.module

    if output_dir == "":
        output_dir = testbench.module.path

    testbench.export(output_dir, "rtv")
    print(f"RTV exported in {output_dir}")


@cli.command()
@click.argument("testbench_path")
@click.option("output_dir", "--output", "-o", default="", help="Output directory")
def doc(testbench_path: str, output_dir: str = ""):
    """Generate both rtv and dtv for given .testbench file"""
    testbench = TestBench(testbench_path=testbench_path)

    if testbench.module is not None and output_dir == "":
        path = testbench.module.path
    elif output_dir != "":
        path = output_dir
    else:
        return

    testbench.export(path, "dtv")
    testbench.export(path, "rtv")
    print(f"DTV/RTV exported in {path}")


@cli.command
@click.argument("rst_path")
@click.option("output_file", "--output", "-o", default="", help="Output file")
def odt(rst_path: str, output_file: str = ""):
    """Convert rst file to odt file"""
    if output_file == "":
        output_file = os.path.abspath(rst_path.replace(".rst", ".odt"))
    rst2odt(rst_path, output_file)


@cli.command
@click.argument("testbench_path")
def ls(testbench_path: str):  # pylint: disable=invalid-name
    """list test in file"""
    testbench = TestBench(testbench_path=testbench_path, _category="batch")

    if len(testbench.test_suite.tests) == 0:
        print(f"No test found in file {testbench_path}")
        return

    print(f"{len(testbench.test_suite.tests)} tests found")
    for test in testbench.test_suite.tests:
        print(test.package.name_from_source)


@cli.command
@click.argument("testbench_path")
def tree(testbench_path: str):
    """list test in file grouped by directory"""
    testbench = TestBench(testbench_path=testbench_path, _category="batch")
    grouped_tests = testbench.test_suite.group_tests()

    len_test = len(testbench.test_suite.tests)
    if len_test == 0:
        print(f"No tests found in file {testbench_path}")
        return

    print(f"{len_test} test found\n")
    for key, tests in grouped_tests.items():
        print(f"{key}:")

        for test in tests:
            print(f" |  {test.package.last_name}")

        print("\n")


if __name__ == "__main__":
    cli()
