# pylint: disable=empty-docstring, missing-class-docstring,
# pylint: disable=missing-function-docstring, missing-module-docstring
import os
import re
import subprocess
import sys
from dataclasses import fields, is_dataclass
from itertools import zip_longest
from typing import Any, Dict, Generator, List, Protocol, Tuple

from bs4 import BeautifulSoup


def get_original_bases(cls):
    """from python 3.12: https://github.com/python/typing/"""
    try:
        return cls.__orig_bases__
    except AttributeError:
        try:
            return cls.__bases__
        except AttributeError:
            raise TypeError(
                f"Expected an instance of type, not {type(cls).__name__!r}"
            ) from None


class SupportsWrite(Protocol):
    """ """

    def write(self, text: str) -> Any:
        ...


# ============================================================================
#
#       Dataclass Helpers
#
# ============================================================================


def walk(obj: Any, path: List[str]) -> Generator[Tuple[List, Any], None, None]:
    """ """
    yield path, obj

    if is_dataclass(obj):
        for fld in fields(obj):
            path.append(fld.name)
            yield from walk(getattr(obj, fld.name), path)
            path.pop()

    elif isinstance(obj, Dict):
        for key, value in obj.items():
            path.append(key)
            yield from walk(value, path)
            path.pop()

    elif isinstance(obj, (list, tuple)):
        for idx, item in enumerate(obj):
            path.append(str(idx))
            yield from walk(item, path)
            path.pop()


def walk_test_suite(t_s_1, t_s_2):
    """ """
    for (path, obj), (dpath, dobj) in zip_longest(
        walk(t_s_1, []), walk(t_s_2, []), fillvalue=([], None)
    ):
        joined_path = ".".join(path)
        joined_dpath = ".".join(dpath)
        obj_ = type(obj) if is_dataclass(obj) or isinstance(obj, list) else obj
        dobj_ = type(dobj) if is_dataclass(dobj) or isinstance(dobj, list) else dobj
        if joined_path != joined_dpath or obj_ != dobj_:
            print(
                repr(joined_path),
                repr(joined_dpath),
                joined_dpath == joined_path,
                obj_,
                obj_ == dobj_,
            )


# ============================================================================
#
#       Sphinx Helpers
#
# ============================================================================


def setup_sphinx(
    basedir: str,
    project: str,
    sphinx_quickstart: str,
    module: str,
    language: str = "en",
):
    """ """
    python = sys.executable
    cmd = " ".join(
        [
            python,
            "-m",
            sphinx_quickstart,
            "--ext-autodoc",
            "-a",
            "ModuleTester",
            "-p",
            project,
            "-l",
            language,
            "--quiet",
            basedir,
        ]
    )

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while proc.returncode is None:
        try:
            outs, errs = proc.communicate(timeout=0.5)
            print(
                (
                    f"[STDOUT] > {outs.decode('utf-8')}"
                    f"[STDERR] > {errs.decode('utf-8')}"
                )
            )
        except subprocess.TimeoutExpired:
            pass

    with open(f"{basedir}\\conf.py", "a", encoding="utf-8") as conf_file:
        conf_file.write(f"import sys\nsys.path.append({module[0]})")


def exec_rst(
    sphinx_build: str,
    rst_path: str,
    builddir: str,
    configdir: str = "",
):
    """ """
    python = sys.executable
    cmd_configdir = []
    if configdir != "":
        cmd_configdir = ["-c", configdir]
    cmd = " ".join([python, "-m", sphinx_build, *cmd_configdir, rst_path, builddir])

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while proc.returncode is None:
        try:
            outs, errs = proc.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass

    print(outs, errs)


def parse_html(html_path: str, dtv_path: str):
    """Removes the navbar from the index.html file"""
    soup = None
    with open(html_path, "r", encoding="utf-8") as html_doc:
        soup = BeautifulSoup(html_doc, "html.parser")

        navsidebar = soup.find("div", attrs={"class": "sphinxsidebar"})
        if navsidebar is not None:
            navsidebar.replaceWith("")

        footer = soup.find("div", attrs={"class": "footer"})
        if footer is not None:
            footer.replaceWith("")

    with open(dtv_path, "w", encoding="utf-8") as html_doc:
        html_doc.write(soup.prettify())


# ============================================================================
#
#       PNG Retriever
#
# ============================================================================


def image_walker(origin):
    dirs = []

    for path, _, files in os.walk(origin):
        for file_ in files:
            if file_.endswith(".png"):
                dirs.append((file_, path))

    return dirs


def get_image_path(file_name, dirs):
    image_name_re = re.compile(f"{file_name}_[0-9]{{2}}.png")
    images = []
    for file_, path in dirs:
        if re.match(image_name_re, file_) is not None:
            image = os.path.abspath(os.path.join(path, file_))
            images.append(image)

    return images


# ============================================================================
#
#       File conversion
#
# ============================================================================


def rst2odt(source: str, dest: str):
    """ """
    python = sys.executable
    script = os.path.join(sys.base_prefix, "Scripts", "rst2odt.py")

    proc = subprocess.Popen(" ".join([python, script, source, dest]))

    while proc.returncode is None:
        try:
            _ = proc.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass


def rst2html(source: str, dest: str):
    """ """
    python = sys.executable
    script = os.path.join(sys.base_prefix, "Scripts", "rst2html.py")

    proc = subprocess.Popen(" ".join([python, script, source, dest]))

    while proc.returncode is None:
        try:
            _ = proc.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass


# ============================================================================
#
#       Formatting
#
# ============================================================================


def format_header(title, delim):
    len_title = len(title)
    line = delim * len_title
    return f"{line}\n{title}\n{line}\n\n"


# class FileState(Enum):  # manager
#     UNTRACKED = 0
#     SAVED = 1
#     MODIFIED = 2


# class TestState(Enum):  # Test
#     LOADED = 0  # * _proc is None and fields are the same as in the template
#     RUNNING = 1  # * _proc is not None
#     FIELDS_MODIFIED = 2  # * _proc is None and fields have been changed
