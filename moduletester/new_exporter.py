"""Jinja2-based document exporter for test results and test lists."""

from __future__ import annotations

import os
import threading
from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

import pypandoc
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from moduletester import config
from moduletester.config import _

_export_conf = config.PACKAGE_CONF["export"]

DEFAULT_TEMPLATE_LOADER = FileSystemLoader(searchpath=_export_conf.template_dir)
JINJA_ENV = Environment(
    loader=DEFAULT_TEMPLATE_LOADER,
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
JINJA_ENV.globals["_"] = _

FMT_TO_EXTENSION = {
    "html": "html",
    "docx": "docx",
    "odt": "odt",
    "rst": "rst",
    "md": "md",
    "markdown": "md",
    "markdown_mmd": "md",
    "markdown_github": "md",
    "markdown_strict": "md",
    "pdf": "pdf",
    "latex": "tex",
    "tex": "tex",
}

DEFAULT_TEMPLATE_NAME = _export_conf.test_results_template_name
DEFAULT_DOCX_REFERENCE = _export_conf.get_docx_ref()

DEFAULT_ODT_REFERENCE = _export_conf.get_odt_ref()

DEFAULT_CSS_STYLE = _export_conf.get_css_style()

DEFAULT_HEADER_SHIFT = _export_conf.docstrings_header_shift

DEFAULT_TOC_DEPTH = _export_conf.toc_depth


@dataclass
class DocumentExporter(ABC):
    """BaseClass for document exportation. To define specific documents, you should
    inherit from this class and define the template_name attribute.
    If the template_name is the default one, the class will search for a template
    corresponding to [class name]_template.j2 in the template directory.
    If the template is found, it will be loaded and used as"""

    template_name: str = DEFAULT_TEMPLATE_NAME
    reload_template: bool = False
    resource_path: Optional[str] = None
    docstrings_header_shift = DEFAULT_HEADER_SHIFT
    toc_depth = DEFAULT_TOC_DEPTH
    _template: Template = field(
        init=False, default=JINJA_ENV.get_template(template_name)
    )
    _docx_reference: str = field(init=False, default=DEFAULT_DOCX_REFERENCE)
    _odt_reference: str = field(init=False, default=DEFAULT_ODT_REFERENCE)
    _css_style: str = field(init=False, default=DEFAULT_CSS_STYLE)

    def render_html(self, with_toc=False) -> str:
        """Render the document as html with or without a table of content.

        Args:
            with_toc: Insert a table of content. Defaults to False.

        Returns:
            generated html string
        """
        extra_args = [
            "--embed-resources",
            "--standalone",
            f"--css={self._css_style}",
        ]
        if with_toc:
            extra_args.extend(["--toc", f"--toc-depth={self.toc_depth}"])

        if self.reload_template:
            self._template = JINJA_ENV.get_template(self.template_name)

        if self.resource_path is not None:
            extra_args.append(f"--resource-path={self.resource_path}")

        return pypandoc.convert_text(
            self._template.render(doc_obj=self),
            to="html",
            format="html",
            extra_args=extra_args,
        )

    def export(
        self, filename: str, fmt="html", extra_args: Optional[list[str]] = None
    ) -> None:
        """Export the document to a file in the specified format.

        Args:
            filename: The name of the file to write to.
            fmt: The format to export to. Defaults to "html".
            extra_args: Additional arguments to pass to pandoc. Defaults to None.
        """
        if extra_args is None:
            extra_args = []
        if fmt == "html":
            self.export_html(filename)
            return

        pypandoc.convert_text(
            self.render_html(),
            fmt,
            format="html",
            outputfile=filename,
            extra_args=extra_args,
        )

    def export_html(self, filename: str) -> None:
        """Export the document to a file in html format.

        Args:
            filename: The name of the file to write to.
        """
        with open(filename, "w", encoding="utf-8") as f:
            d = self.render_html(with_toc=True)
            f.write(d)

    def export_docx(self, filename: str) -> None:
        """Export the document to a file in docx format.

        Args:
            filename: The name of the file to write to.
        """
        extra_args = [
            f"--reference-doc={self._docx_reference}",
            "--toc",
            f"--toc-depth={self.toc_depth}",
        ]

        self.export(filename, "docx", extra_args=extra_args)

    def export_odt(self, filename: str) -> None:
        """Export the document to a file in odt format.

        Args:
            filename: The name of the file to write to.
        """
        extra_args = [
            f"--reference-doc={self._odt_reference}",
            "--toc",
            f"--toc-depth={self.toc_depth}",
        ]
        self.export(filename, "odt", extra_args=extra_args)

    def export_rst(self, filename: str) -> None:
        """Export the document to a file in rst format.

        Args:
            filename: The name of the file to write to.
        """
        self.export(filename, "rst")

    def export_md(self, filename: str) -> None:
        """Export the document to a file in markdown format.

        Args:
            filename: The name of the file to write to.
        """
        self.export(
            filename,
            "markdown-raw_html-native_divs-native_spans-fenced_divs-bracketed_spans-escaped_line_breaks",
        )

    def export_pdf(self, filename: str) -> None:
        """Export the document to a file in pdf format.

        Args:
            filename: The name of the file to write to.
        """
        self.export(
            filename,
            "pdf",
            extra_args=[
                "--pdf-engine=xelatex",
                "--toc",
                f"--toc-depth={self.toc_depth}",
                f"--css={self._css_style}",
            ],
        )

    def _export_with_callback(
        self,
        filename: str,
        fmt: str,
        extra_args: Optional[list[str]],
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Export the document to a file in the specified format and call the callback
        function when the export is complete.

        Args:
            filename: The name of the file to write to.
            fmt: The format to export to.
            extra_args: Additional arguments to pass to pandoc.
            callback: The function to call when the export is complete.
        """
        if extra_args is None:
            extra_args = []
        self.export(filename, fmt, extra_args=extra_args)
        if callback is not None:
            callback()

    def export_docx_async(
        self, filename: str, callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Export the document to a file in docx format in a separate thread.

        Args:
            filename: The name of the file to write to.
            callback: Callback to call once the export is finished. Defaults to None.
        """
        extra_args = [
            f"--reference-doc={self._docx_reference}",
            "--toc",
            f"--toc-depth={self.toc_depth}",
        ]
        t = threading.Thread(
            target=self._export_with_callback,
            args=(filename, "docx", extra_args, callback),
        )
        t.start()

    def export_html_async(
        self, filename: str, callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Export the document to a file in html format in a separate thread.

        Args:
            filename: The name of the file to write to.
            callback: Callback to call once the export is finished. Defaults to None.
        """
        threading.Thread(
            target=self._export_with_callback, args=(filename, "html", None, callback)
        ).start()

    def multi_exports(self, fmts: Iterable[str], basename: str):
        """Export the document to multiple formats successively.

        Args:
            fmts: The formats to export to.
            basename: The base name of the files to write to.

        Raises:
            ValueError: If an unknown format is specified.
        """
        for fmt in fmts:
            if fmt not in FMT_TO_EXTENSION:
                raise ValueError(f"Unknown format {fmt}")
            export_method = getattr(self, f"export_{fmt}")
            export_method(f"{basename}.{fmt}")
            print(f"Export of {basename}.{fmt} complete")

    def multi_exports_async(
        self,
        fmts: Iterable[str],
        basename: str,
        callback: Optional[Callable[[], None]] = None,
    ):
        """Export the document to multiple formats successively in a separate thread.

        Args:
            fmts: The formats to export to.
            basename: The base name of the files to write to.
            callback: Callback to call once the export is finished. Defaults to None.
        """

        def _multi_exports_async(
            fmts: Iterable[str], basename: str, callback: Optional[Callable[[], None]]
        ):
            self.multi_exports(fmts, basename)
            if callback is not None:
                callback()

        threading.Thread(
            target=_multi_exports_async, args=(fmts, basename, callback)
        ).start()

    @classmethod
    def __init_subclass__(cls) -> None:

        if os.path.exists(os.path.join(_export_conf.template_dir, cls.template_name)):
            cls.load_template()

    @classmethod
    def load_template(cls) -> None:
        """Load the Jinja2 template from the configured directory."""
        cls._template = JINJA_ENV.get_template(cls.template_name)
