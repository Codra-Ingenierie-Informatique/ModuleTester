from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from jinja2 import FileSystemLoader

from moduletester import config
from moduletester.new_exporter import JINJA_ENV, DocumentExporter

from .model import Test, TestSuite


@dataclass
class _TestExporter(DocumentExporter):
    test_suite: Optional[TestSuite] = None
    _image_dirs: list[str] = field(init=False, default_factory=list)

    def __post_init__(self):
        global JINJA_ENV
        conf = config.PACKAGE_CONF["export"]
        # if self.test_suite is not None:
        #     if (
        #         templ := getattr(
        #             conf, f"{self.__class__.__name__.lower()}_template_name", None
        #         )
        #     ) is not None and self.template_name != templ:
        #         new_template_loader = FileSystemLoader(searchpath=conf.template_dir)
        #         JINJA_ENV.loader = new_template_loader
        #         self.template_name = templ
        #         self._template = JINJA_ENV.get_template(self.template_name)
        # else:
        #     raise ValueError(
        #         "Configuration is missing key "
        #         f"{self.__class__.__name__.lower()}_template_name.\n"
        #         "Update file config.py and moduletester.ini to add the key."
        #     )

        self._docx_reference = conf.get_docx_ref()
        self._odt_reference = conf.get_odt_ref()
        self._css_style = conf.get_css_style()
        self.docstrings_header_shift = conf.docstrings_header_shift
        self.toc_depth = conf.toc_depth
        self.resource_path = self.test_suite.package.path

        # Updating the template directory in the jinja environment
        new_template_loader = FileSystemLoader(searchpath=conf.template_dir)
        JINJA_ENV.loader = new_template_loader

    def get_images_paths(self, test: Test) -> list[str]:
        if self.test_suite is None:
            return []
        return test.get_images(self._image_dirs)


@dataclass
class TestResultsDocument(_TestExporter):
    template_name: str = "test_results_template.j2"


@dataclass
class TestListDocument(_TestExporter):
    template_name: str = "test_list_template.j2"
