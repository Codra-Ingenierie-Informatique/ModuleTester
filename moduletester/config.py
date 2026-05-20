from __future__ import annotations

import configparser
import os
import os.path as osp
from dataclasses import dataclass, field, fields
from typing import Any, Collection, TypedDict

from guidata import configtools
from guidata.configtools import get_translation

APP_NAME = "ModuleTester"
MOD_NAME = "moduletester"
MODULETESTER_CONFIG_NAME = "moduletester.ini"
MODULETESTER_CONFIG_DIR = os.path.dirname(__file__)

configtools.add_image_module_path(MOD_NAME, osp.join("data", "logo"))
configtools.add_image_module_path(MOD_NAME, osp.join("data", "icons"))

DATAPATH = configtools.get_module_data_path(MOD_NAME, "data")

_ = get_translation(MOD_NAME)


class InvalidDataError(Exception):
    """Exception raised for invalid data in configuration file.

    Args:
        message: Explanation of the error
        key: The key of the invalid data
        value: The invalid value
    """

    def __init__(self, message: str, key: str, value: Any) -> None:
        super().__init__(message)
        self.key = key
        self.value = value


class InvalidPathError(InvalidDataError):
    """Exception raised for invalid path in configuration file."""

    pass


class ConfigConflictError(Exception):
    """Exception raised for conflicting configuration arguments.

    Args:
        message: Explanation of the error
        missing_args: The missing arguments
        extra_args: The extra arguments
    """

    def __init__(
        self, message: str, missing_args: Collection[str], extra_args: Collection[str]
    ):
        super().__init__(message)
        self.missing_args = missing_args
        self.extra_args = extra_args


def _validate_path(path: str, key, value) -> str:
    """Validate a path.

    Args:
        path: path to validate
        key: key of the path
        value: value of the path

    Raises:
        InvalidPathError: If the path is not valid

    Returns:
        returns the path if it is valid
    """
    if not osp.exists(path):
        raise InvalidPathError(f"Path {path} is not valid", key, value)
    return path


def _serialize_field(value: Any) -> str:
    """Serialize a field value to a string.

    Args:
        value: value to serialize

    Returns:
        serialized value
    """
    if isinstance(value, (list, tuple)):
        return ", ".join(map(_serialize_field, value))
    if isinstance(value, bool):
        return str(int(value))
    return str(value)


def _check_section(conf_dataclass, **kwargs) -> tuple[set[str], set[str]]:
    """Check if the section arguments are valid.

    Args:
        conf_dataclass: the dataclass of the section

    Returns:
        missing_args: the missing arguments
        extra_args: the extra arguments
    """
    if len(kwargs) == 0:
        return set(), set()

    field_set = set(map(lambda f: f.name, fields(conf_dataclass)))
    arg_set = set(kwargs.keys())

    missing_args = field_set - arg_set
    extra_args = arg_set - field_set
    return missing_args, extra_args


def _resolve_conflicts(
    conf_dataclass,
    section: configparser.SectionProxy,
    missing_args: Collection[str],
    extra_args: Collection[str],
) -> configparser.SectionProxy:
    """Try to resolve conflicting arguments in a section.

    Args:
        conf_dataclass: configuration dataclass
        section: Configparser section to resolve
        missing_args: missing configuration fields in file
        extra_args: extra configuration fields in file

    Returns:
        Resolved section
    """
    if len(missing_args) > 0:
        for arg in missing_args:
            default_value = getattr(conf_dataclass, arg)
            section[arg] = _serialize_field(default_value)

    if len(extra_args) > 0:
        for arg in extra_args:
            del section[arg]

    return section


def _load_conf(config: configparser.ConfigParser, resolve=False) -> None:
    """Load the configuration from a ConfigParser object.

    Args:
        config: ConfigParser object
        resolve: If True, tries to resolve conflicts in the configuration
    """
    for section_name, section_obj in PACKAGE_CONF.items():
        section_values: configparser.SectionProxy = config.setdefault(section_name, {})  # type: ignore
        missing_args, extra_args = _check_section(section_obj, **section_values)
        if len(missing_args) > 0 or len(extra_args) > 0:
            if resolve:
                section_values = _resolve_conflicts(
                    section_obj, section_values, missing_args, extra_args
                )
            else:
                raise ConfigConflictError(
                    f"Conflicting arguments in section {section_name}",
                    missing_args,
                    extra_args,
                )
        PACKAGE_CONF[section_name] = type(section_obj)(
            **section_values
        )  # reset section


def load_package_conf(
    package_path: str, filename=MODULETESTER_CONFIG_NAME, resolve=False
) -> None:
    """Tries to load the configuration from a file.

    Args:
        package_path: path to the package where the configuration file should be located
        filename: File name to search in package directory. Defaults to
         MODULETESTER_CONFIG_NAME.
        resolve: Try to resolve confilcts if some are found. Defaults to False.
    """
    global MODULETESTER_CONFIG_DIR
    custom_config_file = os.path.join(package_path, filename)

    config = configparser.ConfigParser()
    MODULETESTER_CONFIG_DIR = os.path.abspath(package_path)
    if os.path.isfile(custom_config_file):
        config.read(custom_config_file)

    _load_conf(config, resolve)


def load_conf_from_string(conf_str: str, resolve=False) -> None:
    """Load the configuration from a string.

    Args:
        conf_str: Configuration string
        resolve: Try to resolve conflicts if some are found. Defaults to False.
    """
    config = configparser.ConfigParser()
    config.read_string(conf_str)
    _load_conf(config, resolve)


@dataclass
class GeneralConf:
    """Dataclass for general moduletester parameters"""

    docstring_fmt: str = "rst"
    category: str = "visible"


@dataclass
class ExporterConf:
    """Dataclass for moduletester exporter parameters"""

    template_dir: str = os.path.join(MODULETESTER_CONFIG_DIR, "default_templates")
    test_results_template_name: str = "test_results_template.j2"
    test_list_template_name: str = "test_list_template.j2"
    docx_reference: str = "custom-reference.docx"
    odt_reference: str = "custom-reference.odt"
    css_style: str = "default_style.css"
    export_fmts: list[str] = field(default_factory=lambda: ["html", "docx"])
    reload_templates_on_export: bool = False
    docstrings_header_shift: int = 3
    toc_depth: int = 2

    def __post_init__(self):
        self.template_dir = _validate_path(
            self.get_template_dir(), key="template_dir", value=self.template_dir
        )
        _ = _validate_path(
            self.get_docx_ref(), key="docx_reference", value=self.docx_reference
        )
        _ = _validate_path(
            self.get_odt_ref(), key="odt_reference", value=self.odt_reference
        )
        _ = _validate_path(self.get_css_style(), key="css_style", value=self.css_style)

        _ = _validate_path(
            osp.join(self.template_dir, self.test_results_template_name),
            key="test_results_template_name",
            value=self.test_results_template_name,
        )
        _ = _validate_path(
            osp.join(self.template_dir, self.test_list_template_name),
            key="dv_template_name",
            value=self.test_list_template_name,
        )
        self.reload_templates_on_export = bool(int(self.reload_templates_on_export))
        self.docstrings_header_shift = int(self.docstrings_header_shift)
        self.toc_depth = int(self.toc_depth)

        export_fmts = self.export_fmts
        if isinstance(export_fmts, str):
            export_fmts = export_fmts.replace(" ", "").split(",")

        self.export_fmts = export_fmts

    def get_template_dir(self) -> str:
        return os.path.join(MODULETESTER_CONFIG_DIR, self.template_dir)

    def get_docx_ref(self) -> str:
        return osp.join(self.template_dir, self.docx_reference)

    def get_odt_ref(self) -> str:
        return osp.join(self.template_dir, self.odt_reference)

    def get_css_style(self) -> str:
        return osp.join(self.template_dir, self.css_style)

    def _to_abs_path(self, relative_path: str) -> str:
        return osp.join(osp.abspath(self.template_dir), relative_path)


@dataclass
class GuiConf:
    """Dataclass for moduletester GUI parameters"""

    test_list_visible: bool = True
    test_list_pos: str = "left"
    test_props_visible: bool = True
    test_props_pos: str = "right"
    result_tab_visible: bool = True
    result_tab_pos: str = "bottom"
    result_props_visible: bool = True
    result_props_pos: str = "right"
    cli_visible: bool = False
    cli_pos: str = "bottom"
    toolbox_visible: bool = False
    toolbox_pos: str = "bottom"

    def __post_init__(self):
        self.test_list_visible = bool(int(self.test_list_visible))
        self.test_props_visible = bool(int(self.test_props_visible))
        self.result_tab_visible = bool(int(self.result_tab_visible))
        self.result_props_visible = bool(int(self.result_props_visible))
        self.cli_visible = bool(int(self.cli_visible))
        self.toolbox_visible = bool(int(self.toolbox_visible))


class ConfModel(TypedDict):
    """Dict of package configuration parameters to use as a model"""

    general: GeneralConf
    export: ExporterConf
    gui: GuiConf


def new_config() -> ConfModel:
    """Returns a new default config

    Returns:
        dict: default configuration
    """
    return {
        "general": GeneralConf(),
        "export": ExporterConf(),
        "gui": GuiConf(),
    }


# Default initialization
PACKAGE_CONF: ConfModel = new_config()


def serialize_conf_obj(conf: ConfModel) -> configparser.ConfigParser:
    """Serialize a ConfModel TypedDict to a ConfigParser object.

    Args:
        conf: ConfModel TypedDict to transform to ConfigParser object

    Returns:
        ConfigParser object
    """
    config = configparser.ConfigParser()
    for section_name, section_obj in conf.items():
        config.add_section(section_name)
        for key, value in section_obj.__dict__.items():
            config.set(section_name, key, _serialize_field(value))
    return config


def conf_obj_to_str(conf: ConfModel) -> str:
    """Serialize a ConfModel TypedDict object to a string.

    Args:
        conf: ConfModel TypedDict to serialize to string

    Returns:
        serialized string
    """
    lines = []
    for section_name, section_obj in conf.items():
        lines.append(f"[{section_name}]")
        for key, value in section_obj.__dict__.items():
            if isinstance(value, (list, tuple)):
                value = ", ".join(value)
            if isinstance(value, bool):
                value = str(int(value))
            lines.append(f"{key} = {value}")
        lines.append("")
    return "\n".join(lines)


def save_config(conf: ConfModel, filename: str) -> None:
    global PACKAGE_CONF
    PACKAGE_CONF.update(conf)
    with open(filename, "w") as f:
        serialize_conf_obj(conf).write(f)


def reset_config(self):
    global PACKAGE_CONF
    PACKAGE_CONF.update(new_config())
