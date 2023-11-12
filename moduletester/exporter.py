# pylint: disable=empty-docstring, missing-class-docstring, fixme
# pylint: disable=missing-function-docstring, missing-module-docstring
# guitest: skip

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .model import Module, ResultEnum, Test, TestResult, TestSuite
from .python_helpers import format_header, image_walker

TEMPLATE_ROW = """\
\t{title:<{len_title}}  .. include {path_to_desc}
\t{blank:<{len_title}}      :parser: rst
"""


@dataclass
class TestExporter:
    temp_path: str
    padding: int

    def export(
        self, package: Module, test_description: str, test_images: List[str]
    ) -> Tuple[str, List[str]]:
        """ """
        title = f"**{package.last_name}**"

        desc_path = self.export_description(package, test_description)
        images, substitutes = self.export_images(test_images)

        title = f"\t{title:<{self.padding}}"
        description = (
            f"  .. include:: {desc_path}\n\t{' ' * (self.padding+2)}\t:parser: rst\n\n"
        )

        template = "".join([title, description, *images])

        return template, substitutes

    def export_description(self, package: Module, description: str) -> str:
        """ """
        desc_content = description + "\n\n|\n"

        file_name = f"{package.module.__name__}_dtv.rst"
        path = os.path.join(self.temp_path, file_name)

        with open(path, "w", encoding="utf-8") as tempfile:
            tempfile.write(desc_content)

        return path

    def export_images(self, images: List[str]) -> Tuple[List[str], List[str]]:
        """ """
        image_strings = []
        image_subs = []
        for image in images:
            # Process image path (relative path and name)
            image_path = self.get_image_relpath(image, pathsep=r"\\")
            image_name, _ = os.path.splitext(os.path.basename(image_path))

            image_strings.append(f"\t{' ' * self.padding}  |{image_name}|\n\n")
            image_sub = f".. |{image_name}| image:: {image_path}\n\t:width: 20%\n"
            image_subs.append(image_sub)

        return image_strings, image_subs

    def get_image_relpath(self, image_path: str, pathsep: Optional[str] = None) -> str:
        """ """
        start_path = os.path.join(self.temp_path, os.path.pardir)
        image_relpath = os.path.relpath(image_path, start=start_path)
        if pathsep is not None:
            image_relpath = image_relpath.replace("\\", pathsep)

        return image_relpath


@dataclass
class TestResultExporter:
    temp_path: str
    padding_name: int
    padding_result: int

    def export(self, package: Module, result: TestResult) -> str:
        """ """
        name = f"**{package.last_name}**"

        if result is not None:
            pad_to_desc = self.padding_name + self.padding_result + 4
            temp_path = self.export_comment(package, result)

            result_name = result.result_name
            desc = f".. include:: {temp_path}\n\t{' ' * pad_to_desc}\t:parser: rst\n\n"
        else:
            result_name = "NOT EXECUTED"
            desc = " - \n\n"

        title = f"\t{name:<{self.padding_name}}"
        result = f"{result_name:<{self.padding_result}}"

        export = "  ".join([title, result, desc])
        return export

    def export_comment(self, package: Module, result: TestResult) -> str:
        """ """
        name = f"{package.module.__name__}_rtv.rst"
        path = os.path.join(self.temp_path, name)

        if result is not None:
            comment = result.comment if result.comment != "" else " - \n\n"
        else:
            comment = " - \n\n"

        with open(path, "w", encoding="utf-8") as tempfile:
            tempfile.write(comment)

        return path


@dataclass
class TestSuiteExporter:
    test_suite: TestSuite

    def __post_init__(self):
        origin_path = os.path.abspath(
            os.path.join(self.test_suite.package.path, os.pardir)
        )
        self.image_dirs = image_walker(origin_path)

    def export(self, rst_path: str, temp_path: str, section_callback) -> None:
        """ """
        content = []
        header = format_header(self.test_suite.package_name, "=")
        grouped_tests = self.test_suite.group_tests()

        for group_package, test_list in grouped_tests.items():
            section = section_callback(group_package, test_list, temp_path)
            content.append(section)

        rst_file_content = "".join([header, *content])
        self.write_rst(rst_path, rst_file_content)

    def write_rst(self, rst_path: str, rst_content: str) -> None:
        """ """
        with open(rst_path, "w", encoding="utf-8") as index_rst:
            index_rst.write(rst_content)

    def export_section_dtv(
        self, package: str, tests: List[Test], temp_rst_path: str
    ) -> str:
        """ """
        # Indentation value required for alignement in the table
        max_len = max(len(test.package.last_name) for test in tests) + 4

        header = format_header(package, "-")
        table = self.export_tests_table(tests, max_len, temp_rst_path)

        section = "".join([header, table])

        return section

    def export_tests_table(
        self, tests: List[Test], title_len: int, temp_path: str
    ) -> str:
        """ """
        line = "=" * title_len

        # Generate the content of the table and the list of substitutes
        substitutes = []
        table_content = []
        test_exporter = TestExporter(temp_path, title_len)
        for test in tests:
            test_images = test.get_images(self.image_dirs)
            export, images = test_exporter.export(
                test.package, test.description, test_images
            )
            table_content.append(export)
            substitutes.extend(images)

        # Building the table
        table_directive = ".. table::\n\t:width: 95%\n\t:widths: 25, 55\n\n"
        table_header = f"\t{'Unit':<{title_len}}  Description\n"
        table_border = f"\t{line}  {line}\n"

        table = "".join(
            [
                table_directive,
                table_border,
                table_header,
                table_border,
                *table_content,
                table_border,
                "\n",
                *substitutes,
                "\n\n",
            ]
        )

        return table

    def export_section_rtv(
        self, package: str, tests: List[Test], temp_path: str
    ) -> str:
        """ """
        # Indentation value required for alignement in the table
        name_len = max([len(test.package.last_name) for test in tests]) + 4
        result_len = max([len(result.name) for result in ResultEnum])

        header = format_header(package, "-")
        table = self.export_results_table(tests, name_len, result_len, temp_path)

        section = "".join([header, table])

        return section

    def export_results_table(
        self, tests: List[Test], title_len: int, result_len: int, temp_path: str
    ) -> str:
        """ """
        # Generate the content of the table
        table_content = ""
        result_exporter = TestResultExporter(temp_path, title_len, result_len)
        for test in tests:
            table_content += result_exporter.export(test.package, test.result)

        # Building the table
        table_directive = ".. table::\n\t:widths: 15, 20, 45\n\n"
        table_border = f"\t{'=' * title_len}  {'=' * result_len}  {'=' * title_len}\n"
        table_header = f"\t{'Unit':<{title_len}}  {'Results':<{result_len}}  Remarks\n"

        table = "".join(
            [
                table_directive,
                table_border,
                table_header,
                table_border,
                table_content,
                table_border,
                "\n",
            ]
        )
        return table
